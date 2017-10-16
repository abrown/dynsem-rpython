class Term:
    INT = 0
    REAL = 1
    APPL = 2
    LIST = 3
    VAR = 4
    BLOB = 5

    def matches(self, term):
        return True if isinstance(self, VarTerm) else self == term

    def __init__(self, type):
        self.type = type

    def __str__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class ApplTerm(Term):
    def __init__(self, name, args=None):
        Term.__init__(self, Term.APPL)
        self.name = name
        self.args = args if not args is None else []

    def matches(self, term):
        return self.type == term.type and self.name == term.name and len(self.args) == len(term.args) \
               and all(map(lambda ab: ab[0].matches(ab[1]), zip(self.args, term.args)))

    def __str__(self):
        return self.name if not self.args else "%s(%s)" % (self.name, self.args)


class IntTerm(Term):
    def __init__(self, value):
        Term.__init__(self, Term.INT)
        self.number = value

    def __str__(self):
        return str(self.number)


class VarTerm(Term):
    def __init__(self, name):
        Term.__init__(self, Term.VAR)
        self.name = name

    def __str__(self):
        return str(self.name)
