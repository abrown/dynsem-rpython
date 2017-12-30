from src.meta.context import Context
from src.meta.dynsem import PatternMatchPremise, DynsemError, EqualityCheckPremise, AssignmentPremise, ReductionPremise, \
    CasePremise, Rule, NativeFunction
from src.meta.list_backed_map import ListBackedMap
from src.meta.term import ApplTerm, MapReadTerm, MapWriteTerm, VarTerm, IntTerm

# So that you can still run this module under standard CPython...
try:
    from rpython.rlib.jit import JitDriver, elidable, promote, unroll_safe
except ImportError:
    class JitDriver(object):
        def __init__(self, **kw): pass

        def jit_merge_point(self, **kw): pass

        def can_enter_jit(self, **kw): pass


    def elidable(func):
        return func


    def promote(x):
        return x


    def unroll_safe(func):
        return func


def get_location(term, rule):
    return "%s" % (term.to_string())


# jitdriver = JitDriver(greens=['term', 'rule'], reds='auto', get_printable_location=get_location)
jitdriver = JitDriver(greens=['term', 'rule'], reds=['interpreter'], get_printable_location=get_location)


def jitpolicy(driver):
    try:
        from rpython.jit.codewriter.policy import JitPolicy
        return JitPolicy()
    except ImportError:
        raise NotImplemented("Abandon if we are unable to use RPython's JitPolicy")


# end of RPython setup

class InterpreterError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Interpreter:
    _immutable_fields_ = ['module', 'debug']

    def __init__(self, dynsem_module, debug=0):
        self.environment = ListBackedMap()
        self.module = dynsem_module
        self.debug = debug
        self.nesting = -1

    @unroll_safe
    def interpret(self, term):
        if self.debug:
            self.nesting += 1

        while term is not None and isinstance(term, ApplTerm):
            if self.debug:
                print("%sTerm: %s" % (" " * self.nesting, term.to_string()))

            if not term.trans:
                # TODO this may not work when the term has to match more than one rule
                term.trans = self.find_transformation(term)
            elif self.debug:
                print("%sFound cached rule on: %s" % (" " * self.nesting, term.to_string()))

            transformation = term.trans
            if transformation is None:
                if self.debug:
                    print("%sNo transformation found, returning" % (" " * self.nesting))
                break  # unable to transform this appl, must be terminal
            elif isinstance(transformation, Rule):
                if self.debug:
                    print("%sRule: %s" % (" " * self.nesting, transformation.to_string()))
                if transformation.has_loop:
                    term = self.transform_looping_rule(term, transformation)
                else:
                    term = self.transform_rule(term, transformation)
            elif isinstance(transformation, NativeFunction):
                if self.debug:
                    print("%sNative: %s" % (" " * self.nesting, transformation.to_string()))
                term = self.transform_native_function(term, transformation)
            else:
                raise NotImplementedError()

        if self.debug:
            self.nesting -= 1
        return term

    def find_transformation(self, term):
        for rule in self.module.rules:
            if rule.matches(term):
                return rule
        for native in self.module.native_functions:
            if native.matches(term):
                return native
        return None

    # not sure if I want to: @unroll_safe
    def transform_looping_rule(self, term, rule):
        if self.debug:
            print("%sLooping" % (" " * self.nesting))
        jitdriver.can_enter_jit(term=term, rule=rule, interpreter=self)
        jitdriver.jit_merge_point(term=term, rule=rule, interpreter=self)
        term = promote(term)
        rule = promote(rule)
        return self.transform_rule(term, rule)

    @unroll_safe
    def transform_rule(self, term, rule):
        context = Context(term, rule.number_of_bound_terms)
        # for component in rule.components:
        # context.bind(component, self.environment)
        # TODO re-enable when we can bind the environment name to the context
        context.bind(rule.before, term)
        if self.debug:
            print("%sContext: %s" % (" " * self.nesting, context))

        # handle premises
        if rule.premises:
            for premise in rule.premises:
                self.transform_premise(premise, context)

        # handle environment changes
        if isinstance(rule.after, MapWriteTerm):
            # TODO we incorrectly assume here that there is only one semantic component, an environment map:
            for key in rule.after.assignments:
                value = rule.after.assignments[key]
                if isinstance(value, MapWriteTerm):
                    continue
                resolved_key = context.resolve(key)
                if not isinstance(resolved_key, VarTerm):
                    raise InterpreterError("Expected a VarTerm to use as the environment name but found: %s" %
                                           resolved_key)
                interpreted_value = self.interpret(context.resolve(value))
                if resolved_key.index < 0:
                    resolved_key.index = self.environment.locate(resolved_key.name)
                self.environment.put(resolved_key.index, interpreted_value)
        elif isinstance(rule.after, MapReadTerm):
            # TODO this relies on the same unchecked assumption as above
            resolved_key = context.resolve(rule.after.key)
            if resolved_key.index < 0:
                resolved_key.index = self.environment.locate(resolved_key.name)
            return self.environment.get(resolved_key.index)
        # TODO perhaps the Map*Terms should return not themselves but the saved/retrieved value

        result = context.resolve(rule.after)
        if self.debug:
            print("%sResult: %s" % (" " * self.nesting, result))
        return result

    @unroll_safe
    def transform_premise(self, premise, context):
        if isinstance(premise, PatternMatchPremise):
            if premise.right.matches(premise.left):
                context.bind(premise.left, premise.right)  # TODO seems like it should be context.resolve(premise.right)
            else:
                raise DynsemError("Expected %s to match %s" % (premise.left, premise.right))
        elif isinstance(premise, EqualityCheckPremise):
            # TODO interpret each side here
            left_term = context.resolve(premise.left)
            right_term = context.resolve(premise.right)
            if not left_term.equals(right_term):
                raise DynsemError("Expected %s to equal %s" % (premise.left, premise.right))
        elif isinstance(premise, AssignmentPremise):
            if isinstance(premise.left, VarTerm):
                context.bind(premise.left, context.resolve(premise.right))
            else:
                raise DynsemError("Cannot assign to anything other than a variable (e.g. x => 2); TODO add " +
                                  "support for constructor assignment (e.g. a(1, 2) => a(x, y))")
        elif isinstance(premise, ReductionPremise):
            intermediate_term = context.resolve(premise.left)
            new_term = self.interpret(intermediate_term)
            context.bind(premise.right, new_term)
        elif isinstance(premise, CasePremise):
            value = context.resolve(premise.left)
            found = None
            for i in range(len(premise.values)):
                if premise.values[i] is None:  # otherwise branch
                    found = premise.premises[i]
                    break
                elif premise.values[i].matches(value):
                    found = premise.premises[i]
                    break
            if found:
                self.transform_premise(found, context)
            else:
                raise DynsemError("Unable to find matching branch in case statement: %s" % str(self))
        else:
            raise NotImplementedError()

    @unroll_safe
    def transform_native_function(self, term, native_function):
        context = Context(term, native_function.number_of_bound_terms)
        context.bind(native_function.before, term)

        args = []
        for arg in native_function.before.args:
            resolved = context.resolve(arg)
            interpreted = self.interpret(
                resolved)  # TODO need to determine what type of term to use, not hard-code this
            if not isinstance(interpreted, IntTerm):
                raise InterpreterError("Expected parameter %s of %s to resolve to an IntTerm but was: %s" %
                                       (resolved, native_function, interpreted))
            args.append(interpreted.number)

        if len(args) < 2:
            args.append(0)
        tuple_args = (args[0], args[1])  # TODO RPython demands this

        result = native_function.action(*tuple_args)
        if self.debug:
            print("%sResult: %s" % (" " * self.nesting, result))
        return IntTerm(result)  # TODO need to determine what type of term to use, not hard-code this
