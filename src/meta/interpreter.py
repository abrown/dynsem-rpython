from context import Context
from dynsem import Rule
from src.meta.term import ApplTerm, EnvReadTerm, EnvWriteTerm, VarTerm, SyntaxTerm, ListSyntaxTerm

# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver, elidable, promote
except ImportError:
    class JitDriver(object):
        def __init__(self, **kw): pass

        def jit_merge_point(self, **kw): pass


    def elidable(func):
        return func


    def promote(x):
        return x


def get_location(term):
    return "%s" % (term.to_string())


jitdriver = JitDriver(greens=['term'], reds='auto', get_printable_location=get_location)


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

    def interpret(self, term, context=None):
        while term is not None:
            if self.debug: print("Term: %s" % term.to_string())

            # gross attempt at JIT-ting TODO why can't I put a guard in front of this, like 'isinstance(term, ApplTerm) and term.name == "while"'
            jitdriver.jit_merge_point(term=term)

            if not isinstance(term, SyntaxTerm):
                break  # no need to interpret value terms

            context = context if context else Context()
            if isinstance(term, ApplTerm):
                # TODO shouldn't we resolve here?
                interpreted = ApplTerm(term.name, self.interpret_several(term.args, context))
                transform = self.find(interpreted)
                if not transform:
                    break  # note the permissiveness: we allow some applications to serve as final values
                if isinstance(transform, Rule): # TODO this should not be here, 
                    for var in transform.components:
                        context.bind(var, self.environment)
                term = transform.transform(term, self.interpret)
            elif isinstance(term, VarTerm):
                term = context.resolve(term)
                # break  # TODO really? don't evaluate the resolved term?
            elif isinstance(term, ListSyntaxTerm):
                term = context.resolve(term)
                # break  # TODO really? don't evaluate the resolved term?
            elif isinstance(term, EnvWriteTerm):
                new_environment = {}
                # handle environment cloning first so assignments can overwrite
                for var in term.environments:
                    env = context.resolve(var)
                    new_environment.update(env)
                # overwrite with assignments
                for key in term.assignments:
                    var = context.resolve(VarTerm(key))
                    if not isinstance(var, VarTerm): raise InterpreterError(
                        "Expected a VarTerm to use as the environment name but found: %s" % var)
                    value = term.assignments[key]
                    interpreted_value = self.interpret(value)
                    new_environment[var.name] = interpreted_value
                # save the new environment TODO there could be multiple
                self.environment = new_environment
            elif isinstance(term, EnvReadTerm):
                resolved_key = context.resolve(VarTerm(term.key))
                term = self.environment[resolved_key.name]  # TODO this relies on the same unchecked assumption above

        return term

    def interpret_several(self, terms, context):
        interpreted = []
        for term in terms:
            interpreted.append(self.interpret(term, context))
        return interpreted

    def find(self, term):
        # TODO eventually this will be replaced by a second pass that binds rules to terms
        for rule in self.module.rules:
            if rule.matches(term):
                return rule

        for native in self.module.native_functions:
            if native.matches(term):
                return native

        if self.debug: print("Warning: no transformation found for term %s" % term.to_string())
        return None
