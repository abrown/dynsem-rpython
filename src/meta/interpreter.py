from context import Context
from src.meta.dynsem import EqualityCheckPremise, PatternMatchPremise, AssignmentPremise, ReductionPremise, CasePremise
from src.meta.term import ApplTerm, EnvReadTerm, EnvWriteTerm, VarTerm, ListPatternTerm, ListTerm, IntTerm


class InterpreterError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Interpreter:
    def __init__(self, debug=0):
        self.environment = {}
        self.module = None  # TODO remove this as a parameter from interpret()
        self.debug = debug
        self.nesting = 0

    def interpret(self, mod, term):
        self.module = mod

        while term is not None:
            if self.debug: print("Term: %s" % term.to_string())

            # attempt rule transform
            rule = self.find_rule(term)
            if rule:
                term = self.transform(term, rule)
            else:
                # attempt native transform
                native = self.find_native_function(term)
                if native:
                    term = self.resolve_native(term, native)
                else:
                    # attempt appl transform
                    if isinstance(term, ApplTerm):
                        args = []
                        for arg in term.args:
                            args.append(self.interpret(mod, arg))
                        interpreted_term = ApplTerm(term.name, args)
                        if interpreted_term.equals(term): break  # no change detected after interpreting sub-terms
                        term = interpreted_term
                    else:
                        break  # no need to interpret sub-terms TODO list?

        return term

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

    def transform(self, term, rule):
        if self.debug > 1: print("Rule: %s" % rule.to_string())
        context = Context()
        # for component in rule.components:
        # context.bind(component, self.environment) # TODO re-enable when we can bind the environment name to the context
        context.bind(rule.before, term)

        # handle premises
        if rule.premises:
            for premise in rule.premises:
                self.evaluate_premise(premise, context)

        # handle environment changes
        if isinstance(rule.after, EnvWriteTerm):
            new_environment = {}
            # handle environment cloning first so assignments can overwrite
            for key in rule.after.assignments:
                if isinstance(rule.after.assignments[key], EnvWriteTerm):
                    new_environment.update(self.environment)  # TODO this is an unchecked assumption that {..., E, ...} refers to an E in the semantic components
            # overwrite with assignments
            for key in rule.after.assignments:
                value = rule.after.assignments[key]
                resolved_key = context.resolve(VarTerm(key))
                if not isinstance(resolved_key, VarTerm): raise InterpreterError("Expected a VarTerm to use as the environment name but found: %s" % resolved_key)
                interpreted_value = self.interpret(self.module, context.resolve(value))
                new_environment[resolved_key.name] = interpreted_value
            # save the new environment TODO there could be multiple
            self.environment = new_environment
        elif isinstance(rule.after, EnvReadTerm):
            resolved_key = context.resolve(VarTerm(rule.after.key))
            return self.environment[resolved_key.name]  # TODO this relies on the same unchecked assumption above

        result = context.resolve(rule.after)
        return result

    def evaluate_premise(self, premise, context):
        if isinstance(premise, EqualityCheckPremise):
            left_term = context.resolve(premise.left)
            right_term = context.resolve(premise.right)
            if not left_term.equals(right_term):
                raise InterpreterError("Expected %s to equal %s" % (premise.left, premise.right))
        elif isinstance(premise, PatternMatchPremise):
            if premise.right.matches(premise.left):
                context.bind(premise.left, premise.right)
            else:
                raise InterpreterError("Expected %s to match %s" % (premise.left, premise.right))
        elif isinstance(premise, AssignmentPremise):
            if isinstance(premise.left, VarTerm):
                context.bind(premise.left, context.resolve(premise.right))
            else:
                raise InterpreterError("Cannot assign to anything other than a variable (e.g. x => 2); TODO add " +
                                       "support for constructor assignment (e.g. a(1, 2) => a(x, y))")
        elif isinstance(premise, ReductionPremise):
            intermediate_term = context.resolve(premise.left)
            new_term = self.interpret(self.module, intermediate_term)
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
                self.evaluate_premise(found, context)
            if not found:
                raise InterpreterError("Unable to find matching branch in case statement: %s" % str(premise))
        else:
            raise NotImplementedError

    def resolve_native(self, term, native_function):
        if self.debug > 1: print("Native: %s" % native_function.to_string())
        context = Context()
        context.bind(native_function.before, term)

        args = []
        for arg in native_function.before.args:
            resolved = context.resolve(arg)
            interpreted = self.interpret(self.module, resolved)  # TODO need to determine what type of term to use, not hard-code this
            if not isinstance(interpreted, IntTerm): raise InterpreterError("Expected parameter %s of %s to resolve to an IntTerm but was: %s" % (resolved, native_function, interpreted))
            args.append(interpreted.number)

        if(len(args) < 2): args.append(0)
        tuple_args = (args[0], args[1])  # TODO RPython demands this

        result = native_function.action(*tuple_args)
        return IntTerm(result)  # TODO need to determine what type of term to use, not hard-code this
