class Exp:
    _immutable_fields_ = ['next', 'code', 'index']

    def __init__(self, next_node, code):
        self.next = next_node
        self.code = code

    def __str__(self):
        return self.__class__.__name__


class Match(Exp):
    def __init__(self, code, next_node, other_node):
        Exp.__init__(self, next_node, code)
        self.other_next = other_node


class MatchType(Match):
    def __init__(self, match_on, next_node, other_node):
        Match.__init__(self, 1, next_node, other_node)
        self.type = match_on


class MatchAppl(Match):
    def __init__(self, match_on, next_node, other_node):
        Match.__init__(self, 2, next_node, other_node)
        self.name = match_on


# class MatchApplArgs(Match):
#     def __init__(self, match_on, next_node, other_node):
#         Match.__init__(self, 3, next_node, other_node)
#         self.args = match_on


class MatchInt(Match):
    def __init__(self, match_on, next_node, other_node):
        Match.__init__(self, 4, next_node, other_node)
        self.number = match_on


class Get(Exp):
    _immutable_fields_ = ['next', 'code', 'index']
    def __init__(self, index, next_node):
        Exp.__init__(self, next_node, 10)
        self.index = index


class New(Exp):
    def __init__(self, term, next_node):
        Exp.__init__(self, next_node, 20)
        self.term = term


class Sum(Exp):
    def __init__(self, value, next_node):
        Exp.__init__(self, next_node, 21)
        self.value = value


class Start(Exp):
    def __init__(self, next_node):
        Exp.__init__(self, next_node, 30)


class End(Exp):
    def __init__(self):
        Exp.__init__(self, None, 31)


class Error(Exp):
    def __init__(self, reason):
        Exp.__init__(self, None, 32)
        self.reason = reason


class Term:
    INT = 0
    REAL = 1
    APPL = 2
    LIST = 3
    HOLE = 4
    BLOB = 5

    def __init__(self, type):
        self.type = type

    def __str__(self):
        return self.__class__.__name__


class Appl(Term):
    def __init__(self, name, args):
        Term.__init__(self, Term.APPL)
        self.name = name
        self.args = args

    def __str__(self):
        return self.name if not self.args else "%s(%s)" % (self.name, self.args)


class Int(Term):
    def __init__(self, value):
        Term.__init__(self, Term.INT)
        self.number = value

    def __str__(self):
        return str(self.number)


def eval_exp(exp, term):
    code = exp.code
    if code == 1:  # MatchType
        return (exp.next, term) if term.type == exp.type else (exp.other_next, term)
    elif code == 2:  # MatchAppl
        return (exp.next, term) if term.name == exp.name else (exp.other_next, term)
    # elif code == 3:  # MatchApplArgs
    #     return (exp.next, term) if term.args == exp.args else (exp.other_next, term)
    elif code == 4:  # MatchInt
        return (exp.next, term) if term.number == exp.number else (exp.other_next, term)
    # ...
    elif code == 10:  # GetApplArg, GetListIndex
        return exp.next, term.args[exp.index]
    # ...
    elif code == 20:  # New
        return exp.next, exp.term
    elif code == 21:  # Sum
        return exp.next, Int(term.number + exp.number)
    # ...
    elif code == 30:  # Start
        return exp.next, term
    elif code == 31:  # End
        return None, term
    elif code == 32:  # Error
        print("error with term: %s" % term)
        return None, term
    else:
        raise NotImplementedError


def interpret(ast, term):
    next_node = ast.next
    while next_node is not None: # not isinstance(next_node, End) and not isinstance(next_node, Error):
        print("#%s \t %s" % (next_node, term))
        next_node, term = eval_exp(next_node, term)
    print("Finished: %s" % term)


def main(argv):
    end = End()
    c_branch = Get(0, MatchInt(3, New(Appl('e', []), end), New(Appl('f', []), end)))
    ast = Start(
        MatchType(Term.APPL,
                  MatchAppl('a',
                            Get(0,
                                MatchType(Term.INT,
                                          Sum(2, c_branch),
                                          Error("Expected integer")
                                          )
                                ),
                            MatchAppl('c',
                                      c_branch,
                                      Error('No rules matched')
                                      )
                            ),
                  Error('Expected an application')
                  )
    )

    interpret(ast, Appl('c', [Int(3)]))
    return 0


if __name__ == "__main__":
    main([])


def target(*args):
    return main, None


# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
# try:
#     from rpython.rlib.jit import JitDriver, elidable, promote
# except ImportError:
#     class JitDriver(object):
#         def __init__(self,**kw): pass
#         def jit_merge_point(self,**kw): pass
#     def elidable(func): return func
#     def promote(x): return x
#
# def get_location(myself) :
#     return "%s" % (myself.toString())
#
# jitdriver = JitDriver(greens=['exp'],reds='auto',
#                       get_printable_location=get_location)
#
# def jitpolicy(driver):
#     from rpython.jit.codewriter.policy import JitPolicy
#     return JitPolicy()