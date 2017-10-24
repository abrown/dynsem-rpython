from context import Context
from src.meta.term import ApplTerm, EnvReadTerm, EnvWriteTerm, VarTerm, IntTerm


# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver, elidable, promote
except ImportError:
    class JitDriver(object):
        def __init__(self,**kw): pass
        def jit_merge_point(self,**kw): pass
    def elidable(func): return func
    def promote(x): return x

def get_location(term) :
    return "%s" % (term.to_string())

jitdriver = JitDriver(greens=['term'],reds='auto', get_printable_location=get_location)

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


class InterpreterError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Interpreter:
    def __init__(self, module, debug=0):
        self.environment = {}
        self.module = module
        self.debug = debug
        self.nesting = 0

    def interpret(self, term):
        while term is not None:
            if self.debug: print("Term: %s" % term.to_string())

            # gross attempt at JIT-ting TODO why can't I put a guard in front of this, like 'isinstance(term, ApplTerm) and term.name == "while"'
            jitdriver.jit_merge_point(term=term)

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
                            args.append(self.interpret(arg))
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
                premise.evaluate(context, self.interpret)

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
                interpreted_value = self.interpret(context.resolve(value))
                new_environment[resolved_key.name] = interpreted_value
            # save the new environment TODO there could be multiple
            self.environment = new_environment
        elif isinstance(rule.after, EnvReadTerm):
            resolved_key = context.resolve(VarTerm(rule.after.key))
            return self.environment[resolved_key.name]  # TODO this relies on the same unchecked assumption above

        result = context.resolve(rule.after)
        return result

    def resolve_native(self, term, native_function):
        if self.debug > 1: print("Native: %s" % native_function.to_string())
        context = Context()
        context.bind(native_function.before, term)

        args = []
        for arg in native_function.before.args:
            resolved = context.resolve(arg)
            interpreted = self.interpret(resolved)  # TODO need to determine what type of term to use, not hard-code this
            if not isinstance(interpreted, IntTerm): raise InterpreterError("Expected parameter %s of %s to resolve to an IntTerm but was: %s" % (resolved, native_function, interpreted))
            args.append(interpreted.number)

        if(len(args) < 2): args.append(0)
        tuple_args = (args[0], args[1])  # TODO RPython demands this

        result = native_function.action(*tuple_args)
        return IntTerm(result)  # TODO need to determine what type of term to use, not hard-code this
