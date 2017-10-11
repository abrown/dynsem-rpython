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

    def __str__(self):
        return self.name if not self.args else "%s(%s)" % (self.name, self.args)


class IntTerm(Term):
    def __init__(self, value):
        Term.__init__(self, Term.INT)
        self.number = value

    def __str__(self):
        return str(self.number)
