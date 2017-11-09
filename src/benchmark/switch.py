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


def interpret(code, operand):
    if code == 1:
        return operand + 1
    elif code == 2:
        return operand + 2
    elif code == 3:
        return operand + 3
    else:
        raise NotImplementedError()


def main(argv):
    if not len(argv) == 2:
        raise RuntimeError("Expect one numeric argument passed, e.g. program 1000")

    program = [1, 3, 2]
    total = int(argv[1])
    accumulator = 0
    for i in range(0, total):
        jitdriver.jit_merge_point()
        for c in program:
            accumulator = interpret(c, accumulator)

    print("%d" % accumulator)
    return 0


if __name__ == "__main__":
    main(sys.argv)


def target(*args):
    return main, None
