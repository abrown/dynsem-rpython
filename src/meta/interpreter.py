from src.meta.context import Context
from src.meta.dynsem import PatternMatchPremise, DynsemError, EqualityCheckPremise, AssignmentPremise, ReductionPremise, \
    CasePremise
from src.meta.term import ApplTerm, MapReadTerm, MapWriteTerm, VarTerm, IntTerm

# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver, elidable, promote, unroll_safe
except ImportError:
    class JitDriver(object):
        def __init__(self, **kw): pass

        def jit_merge_point(self, **kw): pass


    def elidable(func):
        return func


    def promote(x):
        return x


    def unroll_safe(func):
        return func


def get_location(term):
    return "%s" % (term.to_string())


jitdriver = JitDriver(greens=['term'], reds='auto', get_printable_location=get_location)


def jitpolicy(driver):
    try:
        from rpython.jit.codewriter.policy import JitPolicy
        return JitPolicy()
    except ImportError:
        raise NotImplemented("Abandon if we are unable to use RPython's JitPolicy")


class InterpreterError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Interpreter:
    _immutable_fields_ = ['module', 'debug']

    def __init__(self, dynsem_module, debug=0):
        self.environment = {}
        self.module = dynsem_module
        self.debug = debug
        self.nesting = -1

    def interpret(self, term):
        if self.debug:
            self.nesting += 1

        while term is not None and isinstance(term, ApplTerm):
            if self.debug:
                print("Term: %s" % term.to_string())

            # TODO need to guard this some way (perhaps with a new node)
            jitdriver.jit_merge_point(term=term)

            # attempt rule transform
            rule = self.find_rule(term)
            if rule:
                if self.debug:
                    print("Rule: %s" % rule.to_string())
                term = self.transform_rule(term, rule)
            else:
                # attempt native transform
                native = self.find_native_function(term)
                if native:
                    if self.debug:
                        print("Native: %s" % native.to_string())
                    term = self.transform_native_function(term, native)
                else:
                    if self.debug:
                        print("No transformation found, returning")
                    break  # unable to transform this appl, must be terminal

        if self.debug:
            self.nesting -= 1
        return term

    def to_tuple(self, list):
        list = list if list else []
        length = len(list)
        if length == 0:
            return ()
        elif length == 1:
            return (list[0])
        elif length == 2:
            return (list[0], list[1])
        else:
            raise NotImplementedError

    def interpret_subterms(self, term):
        args = []
        for arg in term.args:
            args.append(self.interpret(arg))
        return ApplTerm(term.name, args)

    def find_rule(self, term):
        for rule in self.module.rules:
            if rule.matches(term):
                return rule
        return None

    def find_native_function(self, term):
        for native in self.module.native_functions:
            if native.matches(term):
                return native
        return None

    @unroll_safe
    def transform_rule(self, term, rule):
        context = Context()
        # for component in rule.components:
        # context.bind(component, self.environment)
        # TODO re-enable when we can bind the environment name to the context
        context.bind(rule.before, term)

        # handle premises
        if rule.premises:
            for premise in rule.premises:
                self.transform_premise(premise, context)

        # handle environment changes
        if isinstance(rule.after, MapWriteTerm):
            new_environment = {}
            # handle environment cloning first so assignments can overwrite
            for key in rule.after.assignments:
                if isinstance(rule.after.assignments[key], MapWriteTerm):
                    new_environment.update(self.environment)
                    # TODO this is an unchecked assumption that {..., E, ...} refers to an E in the semantic components
            # overwrite with assignments
            for key in rule.after.assignments:
                value = rule.after.assignments[key]
                resolved_key = context.resolve(key)
                if not isinstance(resolved_key, VarTerm):
                    raise InterpreterError("Expected a VarTerm to use as the environment name but found: %s" %
                                           resolved_key)
                interpreted_value = self.interpret(context.resolve(value))
                new_environment[resolved_key.name] = interpreted_value
            # save the new environment TODO there could be multiple
            self.environment = new_environment
        elif isinstance(rule.after, MapReadTerm):
            resolved_key = context.resolve(rule.after.key)
            return self.environment[resolved_key.name]  # TODO this relies on the same unchecked assumption above

        result = context.resolve(rule.after)
        return result

    def transform_premise(self, premise, context):
        if isinstance(premise, PatternMatchPremise):
            if premise.right.matches(premise.left):
                context.bind(premise.left, premise.right)
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
        context = Context()
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
        return IntTerm(result)  # TODO need to determine what type of term to use, not hard-code this
