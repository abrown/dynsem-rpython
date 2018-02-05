from src.meta.term import ApplTerm

# So that you can still run this module under standard CPython...
try:
    from rpython.rlib.jit import JitDriver, elidable, promote, unroll_safe, jit_debug, we_are_jitted
    from rpython.rlib.objectmodel import compute_hash
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

    def jit_debug(string, arg1=0, arg2=0, arg3=0, arg4=0):
        pass

    def we_are_jitted():
        return False

    def compute_hash(x):
        return hash(x)


def get_location(hashed_term, interpreter):
    return "%d" % hashed_term


jitdriver = JitDriver(greens=['hashed_term', 'interpreter'], reds=['term'], get_printable_location=get_location)


def jitpolicy(driver):
    try:
        from rpython.jit.codewriter.policy import JitPolicy
        return JitPolicy()
    except ImportError:
        raise NotImplemented("Abandon if we are unable to use RPython's JitPolicy")


class Interpreter:
    def interpret(self, term):
        while isinstance(term, ApplTerm):
            jitdriver.jit_merge_point(hashed_term=term.hash, interpreter=self, term=term)
            term_hash = compute_hash(term.name)

