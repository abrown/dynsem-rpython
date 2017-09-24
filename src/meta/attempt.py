class Exp:
    def __init__(self, next_node, code):
        self.next = next_node
        self.code = code

    def __str__(self):
        return self.__class__.__name__


class Match(Exp):
    def __init__(self, code, match_on, next_node, other_node):
        super().__init__(next_node, code)
        self.match_on = match_on
        self.other_next = other_node


class MatchType(Match):
    def __init__(self, match_on, next_node, other_node):
        super().__init__(1, match_on, next_node, other_node)


class MatchAppl(Match):
    def __init__(self, match_on, next_node, other_node):
        super().__init__(2, match_on, next_node, other_node)


class MatchValue(Match):
    def __init__(self, match_on, next_node, other_node):
        super().__init__(3, match_on, next_node, other_node)


class Get(Exp):
    def __init__(self, index, next_node):
        super().__init__(next_node, 10)
        self.index = index


class New(Exp):
    def __init__(self, term, next_node):
        super().__init__(next_node, 20)
        self.term = term


class Sum(Exp):
    def __init__(self, value, next_node):
        super().__init__(next_node, 21)
        self.value = value


class Start(Exp):
    def __init__(self, next_node):
        super().__init__(next_node, 30)


class End(Exp):
    def __init__(self):
        super().__init__(None, 31)


class Error(Exp):
    def __init__(self, reason):
        super().__init__(None, 32)
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
    def __init__(self, name, args=[]):
        super().__init__(Term.APPL)
        self.name = name
        self.value = args

    def __str__(self):
        return self.name if not self.value else "{}({})".format(self.name, self.value)


class Int(Term):
    def __init__(self, value):
        super().__init__(Term.INT)
        self.value = value

    def __str__(self):
        return str(self.value)


def eval_exp(exp, term):
    code = exp.code
    if code == 1:  # MatchType
        return (exp.next, term) if term.type == exp.match_on else (exp.other_next, term)
    elif code == 2:  # MatchAppl
        return (exp.next, term) if term.name == exp.match_on else (exp.other_next, term)
    elif code == 3:  # MatchValue
        return (exp.next, term) if term.value == exp.match_on else (exp.other_next, term)
    # ...
    elif code == 10:  # GetApplArg, GetListIndex
        return exp.next, term.value[exp.index]
    # ...
    elif code == 20:  # New
        return exp.next, exp.term
    elif code == 21:  # Sum
        return exp.next, term + exp.value
    # ...
    elif code == 30:  # Start
        return exp.next, term
    elif code == 31:  # End
        return None, term
    elif code == 32:  # Error
        print("error with term: {}".format(term))
        return None, term


def interpret(ast, term):
    next_node = ast.next
    while next_node is not None:
        print("#{} \t {}".format(next_node, term))
        next_node, term = eval_exp(next_node, term)
    print("Finished: {}".format(term))


def main():
    end = End()
    c_branch = Get(0, MatchValue(3, New(Appl('e'), end), New(Appl('f'), end)))
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

if __name__ == "__main__":
    main()
