from src.meta.list_backed_map import ListBackedMap
from src.meta.term import ApplTerm, IntTerm, ListTerm, VarTerm

# So that you can still run this module under standard CPython...
try:
    from rpython.rlib.jit import JitDriver, elidable, promote, unroll_safe, jit_debug, we_are_jitted
    from rpython.rlib.objectmodel import compute_hash
    from rpython.rlib.rarithmetic import r_uint
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


    class r_uint(int):
        pass


def get_location(hashed_term, interpreter):
    return "%d" % hashed_term


jitdriver = JitDriver(greens=['hashed_term', 'interpreter'], reds=['term'], get_printable_location=get_location)


def jitpolicy(driver):
    try:
        from rpython.jit.codewriter.policy import JitPolicy
        return JitPolicy()
    except ImportError:
        raise NotImplemented("Abandon if we are unable to use RPython's JitPolicy")


WHILE = r_uint(compute_hash('while'))
WHILE2 = r_uint(compute_hash('while2'))
BLOCK = r_uint(compute_hash('block'))
ASSIGN = r_uint(compute_hash('assign'))
RETRIEVE = r_uint(compute_hash('retrieve'))
IFZ = r_uint(compute_hash('ifz'))
WRITE = r_uint(compute_hash('write'))
ADD = r_uint(compute_hash('add'))
SUB = r_uint(compute_hash('sub'))
MUL = r_uint(compute_hash('mul'))
DIV = r_uint(compute_hash('div'))
LEQ = r_uint(compute_hash('leq'))


class Interpreter:
    _immutable_fields_ = ['debug']

    def __init__(self, debug=0):
        self.debug = debug
        self.environment = ListBackedMap()

    def interpret(self, term):
        while isinstance(term, ApplTerm):
            jitdriver.jit_merge_point(hashed_term=term.hash, interpreter=self, term=term)

            if self.debug:
                print(term)
                
            term = self.eval(term)

            if isinstance(term, ApplTerm) and term.has_loop:
                jitdriver.can_enter_jit(hashed_term=term.hash, interpreter=self, term=term)

        return term

    def eval(self, term):
        if term.name_hash == WHILE:
            # while(cond, then) --> while2(cond, value, then) where cond --> value
            cond = term.args[0]
            then = term.args[1]
            value = self.interpret(cond)
            return ApplTerm('while2', [cond, value, then], WHILE2)
        elif term.name_hash == WHILE2:
            if term.args[1].number == 0:
                # while2(cond, 0, then) --> 0
                return IntTerm(0)
            else:
                # while2(cond, value, then) --> while(cond, then) where then --> ignored
                cond = term.args[0]
                then = term.args[2]
                ignored = self.interpret(then)
                return ApplTerm('while', [cond, then], WHILE, True)
        elif term.name_hash == BLOCK:
            # block([x | xs]) --> block(xs) where x --> y
            if len(term.args) == 0:
                return None
            list = term.args[0]
            assert isinstance(list, ListTerm)
            if len(list.items) == 0:
                return None
            x = list.items[0]
            y = self.interpret(x)
            if len(list.items) == 1:
                return ApplTerm('block', [ListTerm()], BLOCK)
            else:
                xs = list.items[1:]
                return ApplTerm('block', [ListTerm(xs)], BLOCK)
        elif term.name_hash == ASSIGN:
            # E |- assign(x, v) --> {x |--> v, E}
            x = term.args[0]
            assert isinstance(x, VarTerm)
            v = self.interpret(term.args[1])
            if x.index < 0:
                x.index = self.environment.locate(x.name)
            self.environment.put(x.index, v)
            return IntTerm(0)
        elif term.name_hash == RETRIEVE:
            # E |- retrieve(x) --> E[x]
            x = term.args[0]
            assert isinstance(x, VarTerm)
            if x.index < 0:
                x.index = self.environment.locate(x.name)
            return self.environment.get(x.index)
        elif term.name_hash == IFZ:
            # ifz(cond, then, else) --> result where cond --> cond2; case cond2 of {0 => result => else otherwise => result => then}
            cond = term.args[0]
            then = term.args[1]
            else_ = term.args[2]
            cond_ = self.interpret(cond)
            if cond_.number == 0:
                result = then
            else:
                result = else_
            return result
        elif term.name_hash == WRITE:
            # native
            s = self.interpret(term.args[0])
            print(s.to_string())
            return IntTerm(0)
        elif term.name_hash == ADD:
            # native
            x = self.interpret(term.args[0])
            y = self.interpret(term.args[1])
            z = x.number + y.number
            return IntTerm(z)
        elif term.name_hash == SUB:
            # native
            x = self.interpret(term.args[0])
            y = self.interpret(term.args[1])
            z = x.number - y.number
            return IntTerm(z)
        elif term.name_hash == MUL:
            # native
            x = self.interpret(term.args[0])
            y = self.interpret(term.args[1])
            z = x.number * y.number
            return IntTerm(z)
        elif term.name_hash == DIV:
            # native
            x = self.interpret(term.args[0])
            y = self.interpret(term.args[1])
            z = x.number // y.number
            return IntTerm(z)
        elif term.name_hash == LEQ:
            # native
            x = self.interpret(term.args[0])
            y = self.interpret(term.args[1])
            z = int(x.number <= y.number)
            return IntTerm(z)
        else:
            raise NotImplementedError
