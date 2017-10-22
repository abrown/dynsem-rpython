class Term:
    def as_string(self):
        return self.__str__()

    def matches(self, term):
        return True if isinstance(self, VarTerm) else self == term

    def __init__(self):
        pass

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

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
        Term.__init__(self)
        self.name = name
        self.args = args if args else []

    def matches(self, term):
        if not isinstance(term, self.__class__) or self.name != term.name or len(self.args) != len(term.args):
            return False
        for i in range(len(self.args)):
            if not self.args[i].matches(term.args[i]): return False
        return True

    def __str__(self):
        args = []
        for a in self.args:
            args.append(str(a))
        return self.name if not self.args else "%s(%s)" % (self.name, ", ".join(args))


class IntTerm(Term):
    def __init__(self, value):
        Term.__init__(self)
        self.number = value

    def __str__(self):
        return str(self.number)


class VarTerm(Term):
    def __init__(self, name):
        Term.__init__(self)
        self.name = name

    def __str__(self):
        return str(self.name)


class EnvTerm(Term):
    def __init__(self, assignments=None):
        Term.__init__(self)
        self.assignments = assignments if assignments else {}

    def __str__(self):
        return str(self.assignments)
