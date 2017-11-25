from src.meta.printable import Printable


class Term(Printable):
    def matches(self, term):
        return True if isinstance(self, VarTerm) else self == term

    def equals(self, term):
        # TODO add to each subclass for rpython
        return isinstance(term, self.__class__)

    def __init__(self):
        pass

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class ApplTerm(Term):
    _immutable_fields = ['name', 'args[*]']

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

    def equals(self, term):
        if not isinstance(term, self.__class__) or self.name != term.name or len(self.args) != len(term.args):
            return False
        for i in range(len(self.args)):
            if not self.args[i].equals(term.args[i]): return False
        return True

    def to_string(self):
        args = []
        for a in self.args:
            args.append(a.to_string())
        return self.name if not self.args else "%s(%s)" % (self.name, ", ".join(args))


class ListTerm(Term):
    _immutable_fields = ['items[*]']

    def __init__(self, items=None):
        Term.__init__(self)
        self.items = items if items else []

    def matches(self, term):
        if not isinstance(term, self.__class__) or len(self.items) != len(term.items):
            return False
        for i in range(len(self.items)):
            if not self.items[i].matches(term.items[i]): return False
        return True

    def equals(self, term):
        if not isinstance(term, self.__class__) or len(self.items) != len(term.items):
            return False
        for i in range(len(self.items)):
            if not self.items[i].equals(term.items[i]): return False
        return True

    def to_string(self):
        args = []
        for a in self.items:
            args.append(a.to_string())
        return "[%s]" % (", ".join(args))


class ListPatternTerm(Term):
    _immutable_fields = ['vars[*]', 'rest']

    def __init__(self, vars=None, rest=None):
        Term.__init__(self)
        self.vars = vars if vars else []
        self.rest = rest

    def matches(self, term):
        if not isinstance(term, ListTerm) or len(self.vars) > len(term.items):
            return False
        else:
            return True

    def to_string(self):
        args = []
        for a in self.vars:
            args.append(a.to_string())
        return "[%s | %s]" % (", ".join(args), self.rest)


class IntTerm(Term):
    _immutable_fields = ['number']

    def __init__(self, value):
        Term.__init__(self)
        self.number = value

    def equals(self, term):
        return isinstance(term, self.__class__) and self.number == term.number

    def matches(self, term):
        return isinstance(term, IntTerm) and self.number == term.number

    def to_string(self):
        return str(self.number)


class VarTerm(Term):
    _immutable_fields = ['name']

    def __init__(self, name):
        Term.__init__(self)
        self.name = name

    def equals(self, term):
        return isinstance(term, self.__class__) and self.name == term.name

    def to_string(self):
        return str(self.name)


class EnvWriteTerm(Term):
    _immutable_fields = ['assignments[*]']

    # TODO this probably shouldn't be a term
    def __init__(self, assignments=None):
        Term.__init__(self)
        self.assignments = assignments if assignments else {}

    def to_string(self):
        args = []
        for key in self.assignments:
            if isinstance(self.assignments[key], EnvWriteTerm):
                args.append(key)
            else:
                args.append("%s |--> %s" % (key, self.assignments[key]))
        return "{%s}" % (", ".join(args))


class EnvReadTerm(Term):
    _immutable_fields = ['name', 'key']

    # TODO this probably shouldn't be a term
    def __init__(self, name, key):
        Term.__init__(self)
        self.name = name  # the environment name
        self.key = key  # the name to retrieve from it

    def to_string(self):
        return "%s[%s]" % (self.name, self.key)
