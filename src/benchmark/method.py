import sys  # for print

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


jitdriver = JitDriver(greens=[], reds='auto')


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


class Exp:
    def call(self, operand):
        return 0

    def __str__(self):
        return self.__class__.__name__


class Add1Exp(Exp):
    def call(self, operand):
        return operand + 1


class Add2Exp(Exp):
    def call(self, operand):
        return operand + 2


class Add3Exp(Exp):
    def call(self, operand):
        return operand + 3


def main(argv):
    if not len(argv) == 2:
        raise RuntimeError("Expect one numeric argument passed, e.g. program 1000")

    program = [Add1Exp(), Add3Exp(), Add2Exp()]
    promote(program)
    total = int(argv[1])
    accumulator = 0
    for i in range(0, total):
        jitdriver.jit_merge_point()
        for e in program:
            accumulator = e.call(accumulator)

    print("%d" % accumulator)
    return 0


if __name__ == "__main__":
    main(sys.argv)


def target(*args):
    return main, None