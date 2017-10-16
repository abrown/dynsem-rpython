from meta.dynsem import *


class InterpreterError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Interpreter:
    @staticmethod
    def interpret(mod, term):
        while term is not None:
            rule = Interpreter.find(term, mod)
            if not rule: break
            term = Interpreter.transform(term, rule)
        return term

    @staticmethod
    def find(term, mod):
        return next((rule for rule in mod.rules if rule.before.matches(term)), None)

    @staticmethod
    def transform(term, rule):
        context = {}
        Interpreter.bind(term, rule.before, context)
        if rule.premises:
            for premise in rule.premises:
                if isinstance(premise, EqualityCheckPremise):
                    if Interpreter.resolve(premise.left, context) != Interpreter.resolve(premise.right, context):
                        raise InterpreterError("Expected {} to equal {}".format(premise.left, premise.right))
                elif isinstance(premise, PatternMatchPremise):
                    if premise.right.matches(premise.left):
                        Interpreter.bind(premise.left, premise.right, context)
                    else:
                        raise InterpreterError("Expected {} to match {}".format(premise.left, premise.right))
                elif isinstance(premise, AssignmentPremise):
                    context[premise.right.value] = Interpreter.resolve(premise.left, context)
                else:
                    raise NotImplementedError()
        return rule.after

    @staticmethod
    def bind(term, pattern, context):
        if isinstance(pattern, VarTerm):
            context[pattern.name] = term
        elif isinstance(pattern, ApplTerm):
            for (term_arg, pattern_arg) in zip(term.args, pattern.args):
                Interpreter.bind(term_arg, pattern_arg, context)


    @staticmethod
    def resolve(term, context):
        if isinstance(term, VarTerm):
            return context[term.name]
        else:
            return term