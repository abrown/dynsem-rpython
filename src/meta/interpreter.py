from src.meta.dynsem import EqualityCheckPremise, PatternMatchPremise, AssignmentPremise, ReductionPremise, CasePremise
from src.meta.term import ApplTerm, EnvReadTerm, EnvWriteTerm, VarTerm


class InterpreterError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Interpreter:
    def __init__(self):
        self.environment = {}
        self.module = None

    def interpret(self, mod, term, debug=False):
        self.module = mod
        while term is not None:
            if debug: print(str(term.as_string()))
            rule = self.find(term)
            if not rule: break
            term = self.transform(term, rule)
        return term

    def find(self, term):
        for rule in self.module.rules:
            if rule.before.matches(term):
                return rule
        return None

    def transform(self, term, rule):
        context = {}
        Interpreter.bind(term, rule.before, context)
        # TODO bind the semantic components as well

        # handle premises
        if rule.premises:
            for premise in rule.premises:
                self.evaluate_premise(premise, context)

        # handle environment changes
        if isinstance(rule.after, EnvWriteTerm):
            new_environment = {}
            for key in rule.after.assignments:
                value = rule.after.assignments[key]
                if isinstance(value, EnvWriteTerm):
                    new_environment.update(
                        self.environment)  # TODO this is an unchecked assumption that {..., E, ...} refers to an E in the semantic components
                else:
                    new_environment[key] = Interpreter.resolve(value, context)
            self.environment = new_environment
        elif isinstance(rule.after, EnvReadTerm):
            return self.environment[rule.after.key]  # TODO this relies on the same unchecked assumption above

        return Interpreter.resolve(rule.after, context)

    def evaluate_premise(self, premise, context):
        if isinstance(premise, EqualityCheckPremise):
            if Interpreter.resolve(premise.left, context) != Interpreter.resolve(premise.right, context):
                raise InterpreterError("Expected %s to equal %s" % (premise.left, premise.right))
        elif isinstance(premise, PatternMatchPremise):
            if premise.right.matches(premise.left):
                Interpreter.bind(premise.left, premise.right, context)
            else:
                raise InterpreterError("Expected %s to match %s" % (premise.left, premise.right))
        elif isinstance(premise, AssignmentPremise):
            if isinstance(premise.left, VarTerm):
                context[premise.left.name] = Interpreter.resolve(premise.right, context)
            else:
                raise InterpreterError("Cannot assign to anything other than a variable (e.g. x => 2); TODO add " +
                                       "support for constructor assignment (e.g. a(1, 2) => a(x, y))")
        elif isinstance(premise, ReductionPremise):
            intermediate_term = Interpreter.resolve(premise.left, context)
            intermediate_rule = self.find(intermediate_term)
            if not intermediate_rule: raise InterpreterError("In a reduction premise, failed to find a rule " +
                                                             "matching: %s" % str(intermediate_term))
            intermediate_term = self.transform(intermediate_term, intermediate_rule)
            Interpreter.bind(intermediate_term, premise.right, context)
        elif isinstance(premise, CasePremise):
            value = Interpreter.resolve(premise.left, context)
            for i in range(len(premise.values)):
                if premise.values[i] is None:  # otherwise branch
                    self.evaluate_premise(premise.premises[i], context)
                elif premise.values[i].matches(value):
                    self.evaluate_premise(premise.premises[i], context)
                else:
                    raise InterpreterError("Unable to find matching branch in case statement: %s" % str(premise))
        else:
            raise NotImplementedError

    @staticmethod
    def bind(term, pattern, context):
        """Bind the names free variables in a pattern to values in a term and save them in a context; TODO make this non-static?"""
        if isinstance(pattern, VarTerm):
            context[pattern.name] = term
        elif isinstance(pattern, ApplTerm):
            if len(term.args) != len(pattern.args): raise InterpreterError(
                "Expected the term and the pattern to have the same number of arguments")
            for i in range(len(term.args)):
                Interpreter.bind(term.args[i], pattern.args[i], context)

    @staticmethod
    def resolve(term, context):
        """Using a context, resolve the names of free variables in a pattern to create a new term; TODO make this non-static?"""
        if isinstance(term, VarTerm) and term.name in context:
            return context[term.name]
        elif isinstance(term, ApplTerm):
            resolved_args = []
            for i in range(len(term.args)):
                resolved_args.append(Interpreter.resolve(term.args[i], context))
            return ApplTerm(term.name, resolved_args)
        else:
            return term
