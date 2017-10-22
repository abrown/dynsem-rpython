from src.meta.dynsem import EqualityCheckPremise, PatternMatchPremise, AssignmentPremise, ReductionPremise, CasePremise
from src.meta.term import ApplTerm, EnvReadTerm, EnvWriteTerm, VarTerm, ListPatternTerm, ListTerm, IntTerm


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
            rule = self.find_rule(term)
            if not rule: break
            term = self.transform(term, rule)
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
                    new_environment[key] = self.resolve(value, context)
            self.environment = new_environment
        elif isinstance(rule.after, EnvReadTerm):
            return self.environment[rule.after.key]  # TODO this relies on the same unchecked assumption above

        return self.resolve(rule.after, context)

    def evaluate_premise(self, premise, context):
        if isinstance(premise, EqualityCheckPremise):
            if self.resolve(premise.left, context) != self.resolve(premise.right, context):
                raise InterpreterError("Expected %s to equal %s" % (premise.left, premise.right))
        elif isinstance(premise, PatternMatchPremise):
            if premise.right.matches(premise.left):
                Interpreter.bind(premise.left, premise.right, context)
            else:
                raise InterpreterError("Expected %s to match %s" % (premise.left, premise.right))
        elif isinstance(premise, AssignmentPremise):
            if isinstance(premise.left, VarTerm):
                context[premise.left.name] = self.resolve(premise.right, context)
            else:
                raise InterpreterError("Cannot assign to anything other than a variable (e.g. x => 2); TODO add " +
                                       "support for constructor assignment (e.g. a(1, 2) => a(x, y))")
        elif isinstance(premise, ReductionPremise):
            intermediate_term = self.resolve(premise.left, context)
            intermediate_rule = self.find_rule(intermediate_term)
            if not intermediate_rule:
                raise InterpreterError("In a reduction premise, failed to find a rule matching: %s" %
                                       str(intermediate_term))
            intermediate_term = self.transform(intermediate_term, intermediate_rule)
            Interpreter.bind(intermediate_term, premise.right, context)
        elif isinstance(premise, CasePremise):
            value = self.resolve(premise.left, context)
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
        """Bind the names free variables in a pattern to values in a term and save them in a context; TODO make this
        non-static?"""
        if isinstance(pattern, VarTerm):
            context[pattern.name] = term
        elif isinstance(pattern, ListPatternTerm):
            for i in range(len(pattern.vars)):
                context[pattern.vars[i].name] = term.items[i]
            rest = term.items[len(pattern.vars):]
            context[pattern.rest.name] = ListTerm(rest)
        elif isinstance(pattern, ApplTerm):
            if len(term.args) != len(pattern.args):
                raise InterpreterError("Expected the term and the pattern to have the same number of arguments")
            for i in range(len(term.args)):
                Interpreter.bind(term.args[i], pattern.args[i], context)

    def resolve(self, term, context):
        """Using a context, resolve the names of free variables in a pattern to create a new term; TODO make this
        non-static?"""
        if isinstance(term, VarTerm) and term.name in context:
            return context[term.name]
        elif isinstance(term, ApplTerm):
            native = self.find_native_function(term)
            if native:
                return self.resolve_native(native, term, context)
            else:
                return self.resolve_appl(term, context)
        elif isinstance(term, ListTerm):
            return self.resolve_list(term, context)
        else:
            return term

    def resolve_native(self, native, term, context):
        args = []
        for arg in term.args:
            resolved = self.resolve(arg, context).number  # TODO need to determine what type of term to use, not hard-code this
            args.append(resolved)
        return IntTerm(native.action(*args))  # TODO need to determine what type of term to use, not hard-code this

    def resolve_appl(self, term, context):
        resolved_args = []
        for arg in term.args:
            resolved_arg = self.resolve(arg, context)
            if isinstance(resolved_arg, ListTerm) and not resolved_arg.items:
                continue  # special case for empty lists; TODO should we dispose of empty lists like this?
            else:
                resolved_args.append(resolved_arg)
        return ApplTerm(term.name, resolved_args)

    def resolve_list(self, term, context):
        resolved_items = []
        for i in range(len(term.items)):
            resolved_items.append(self.resolve(term.items[i], context))
        return ListTerm(resolved_items)
