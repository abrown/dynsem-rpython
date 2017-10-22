import unittest
from dynsem import *
from term import *


class InterpreterError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Interpreter:
    def __init__(self):
        self.environment = {}

    def interpret(self, mod, term, debug=False):
        while term is not None:
            if debug: print(str(term.as_string()))
            rule = self.find(term, mod)
            if not rule: break
            term = self.transform(term, rule)
        return term

    def find(self, term, mod):
        for rule in mod.rules:
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
                        raise InterpreterError(
                            "Cannot assign to anything other than a variable (e.g. x => 2); TODO add support for constructor assignment (e.g. a(1, 2) => a(x, y))")
                else:
                    raise NotImplementedError()

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

    @staticmethod
    def bind(term, pattern, context):
        if isinstance(pattern, VarTerm):
            context[pattern.name] = term
        elif isinstance(pattern, ApplTerm):
            if len(term.args) != len(pattern.args): raise InterpreterError(
                "Expected the term and the pattern to have the same number of arguments")
            for i in range(len(term.args)):
                Interpreter.bind(term.args[i], pattern.args[i], context)

    @staticmethod
    def resolve(term, context):
        if isinstance(term, VarTerm) and term.name in context:
            return context[term.name]
        elif isinstance(term, ApplTerm):
            resolved_args = []
            for i in range(len(term.args)):
                resolved_args.append(Interpreter.resolve(term.args[i], context))
            return ApplTerm(term.name, resolved_args)
        else:
            return term
