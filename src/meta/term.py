from src.meta.printable import Printable


class Term(Printable):
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

    def __init__(self):
        pass

    def walk(self, visitor, accumulator=None):
        return visitor(self, accumulator)

    def walk_list(self, items, visitor, accumulator):
        for item in items:
            result = item.walk(visitor, accumulator)
            if result:
                return result

    def matches(self, term):
        return True if isinstance(self, VarTerm) else self == term

    def equals(self, term):
        # TODO add to each subclass for rpython
        return isinstance(term, self.__class__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


# TODO refactor this into ListTerm
class ApplTerm(Term):
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

    def __init__(self, name, args=None, trans=None):
        Term.__init__(self)
        self.name = name
        self.args = list(args) if args else []
        self.trans = trans  # caches a matched transformation for this term

    def walk(self, visitor, accumulator=None):
        return visitor(self, accumulator) or self.walk_list(self.args, visitor, accumulator)

    def matches(self, term):
        if not isinstance(term, self.__class__) or self.name != term.name or len(self.args) != len(term.args):
            return False
        for i in range(len(self.args)):
            if not self.args[i].matches(term.args[i]):
                return False
        return True

    def equals(self, term):
        if not isinstance(term, self.__class__) or self.name != term.name or len(self.args) != len(term.args):
            return False
        for i in range(len(self.args)):
            if not self.args[i].equals(term.args[i]):
                return False
        return True

    def to_string(self):
        args = []
        for a in self.args:
            args.append(a.to_string())
        return self.name if not self.args else "%s(%s)" % (self.name, ", ".join(args))


class ListTerm(Term):
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

    def __init__(self, items=None):
        Term.__init__(self)
        self.items = list(items) if items else []

    def walk(self, visitor, accumulator=None):
        return self.walk_list(self.items, visitor, accumulator)

    def matches(self, term):
        if not isinstance(term, self.__class__) or len(self.items) != len(term.items):
            return False
        for i in range(len(self.items)):
            if not self.items[i].matches(term.items[i]):
                return False
        return True

    def equals(self, term):
        if not isinstance(term, self.__class__) or len(self.items) != len(term.items):
            return False
        for i in range(len(self.items)):
            if not self.items[i].equals(term.items[i]):
                return False
        return True

    def to_string(self):
        args = []
        for a in self.items:
            args.append(a.to_string())
        return "[%s]" % (", ".join(args))


class ListPatternTerm(Term):
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

    def __init__(self, vars=None, rest=None):
        Term.__init__(self)
        self.vars = list(vars) if vars else []
        self.rest = rest

    def walk(self, visitor, accumulator=None):
        return self.walk_list(self.vars, visitor, accumulator) or visitor(self.rest, accumulator)

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
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

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
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

    def __init__(self, name, slot=-1, index=-1):
        Term.__init__(self)
        self.name = name
        self.slot = slot
        self.index = index

    def equals(self, term):
        return isinstance(term, self.__class__) and self.name == term.name

    def to_string(self):
        return "%s#%d" % (self.name, self.slot)

    def __hash__(self):
        return hash(self.name)


class MapWriteTerm(Term):
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

    def __init__(self, assignments=None):
        Term.__init__(self)
        self.assignments = assignments if assignments else {}

    def walk(self, visitor, accumulator=None):
        result = None
        for a in self.assignments:
            result = visitor(a, accumulator) # TODO store assignment keys as VarTerms
            if result:
                break
            result = visitor(self.assignments[a], accumulator)
            if result:
                break
        return result

    def to_string(self):
        args = []
        for key in self.assignments:
            if isinstance(self.assignments[key], MapWriteTerm):
                args.append(key.to_string())
            else:
                args.append("%s |--> %s" % (key.to_string(), self.assignments[key].to_string()))
        return "{%s}" % (", ".join(args))


class MapReadTerm(Term):
    _immutable_fields = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map', 'key']

    def __init__(self, map, key):
        Term.__init__(self)
        self.map = map  # the map name
        self.key = key  # the key to retrieve from it

    def walk(self, visitor, accumulator=None):
        return visitor(self.map, accumulator) or visitor(self.key, accumulator)

    def to_string(self):
        return "%s[%s]" % (self.map, self.key)
