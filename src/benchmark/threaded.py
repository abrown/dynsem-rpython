import sys  # for print


class Exp:
    def __init__(self, next_node=None):
        self.next = next_node

    def then(self, next_node):
        self.next = next_node

    def __str__(self):
        return self.__class__.__name__


class IsDone(Exp):
    def __init__(self, limit, next_node=None):
        Exp.__init__(self, next_node)
        self.limit = limit


class Increment(Exp):
    def __init__(self, next_node=None):
        Exp.__init__(self, next_node)


def eval_exp(exp, term):
    if isinstance(exp, IsDone):
        return (None, term) if term == exp.limit else (exp.next, term)
    elif isinstance(exp, Increment):
        term += 1
        return exp.next, term
    else:
        raise NotImplementedError


def interpret(ast, term):
    next_node = ast.next
    while next_node is not None:
        next_node, term = eval_exp(next_node, term)
    print("Finished: %s" % term)


def main(argv):
    if not len(argv) == 2:
        raise RuntimeError("Expect one numeric argument passed, e.g. program 1000");

    n = int(argv[1])
    a = IsDone(n)
    b = Increment()
    a.then(b)
    b.then(a)

    interpret(a, 0)
    return 0


if __name__ == "__main__":
    main(sys.argv)


def target(*args):
    return main, None