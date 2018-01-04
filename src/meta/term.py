from src.meta.printable import Printable


class Term(Printable):
    _immutable_fields_ = ['name', 'args[*]', 'items[*]', 'vars[*]', 'rest', 'number', 'slot', 'assignments', 'map',
                          'key']

    def __init__(self, cells=None, var_offsets=None):
        self.cells = cells if cells else []
        self.var_offsets = var_offsets if var_offsets else []

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

    def to_string(self):
        for c in self.cells:
            if


class Cell(Printable):
    _immutable_ = True
    
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


# TODO refactor this into ListTerm
class ApplTerm(Cell):
    def __init__(self, name, size=0, trans=None, bound_terms=None):
        Cell.__init__(self)
        self.name = name
        self.size = size
        self.trans = trans  # caches a matched transformation for this term
        self.bound_terms = bound_terms  # caches the built context for the transformation matching this term

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
        return self.name


class ListTerm(Cell):
    def __init__(self, size=0):
        Cell.__init__(self)
        self.size = size

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
        return "list#%d" % self.size


class ListPatternTerm(Cell):
    def __init__(self, size=0, tail_offset=0):
        Cell.__init__(self)
        self.size = size
        self.tail_offset = tail_offset

    def walk(self, visitor, accumulator=None):
        return self.walk_list(self.vars, visitor, accumulator) or visitor(self.rest, accumulator)

    def matches(self, term):
        if not isinstance(term, ListTerm) or len(self.vars) > len(term.items):
            return False
        else:
            return True

    def to_string(self):
        return "listpattern#%d" % self.size


class IntTerm(Cell):
    def __init__(self, value):
        Cell.__init__(self)
        self.number = value

    def equals(self, term):
        return isinstance(term, self.__class__) and self.number == term.number

    def matches(self, term):
        return isinstance(term, IntTerm) and self.number == term.number

    def to_string(self):
        return str(self.number)


class VarTerm(Cell):
    def __init__(self, name, slot=-1, index=-1):
        Cell.__init__(self)
        self.name = name
        self.slot = slot
        self.index = index

    def equals(self, term):
        return isinstance(term, self.__class__) and self.name == term.name

    def to_string(self):
        return "%s#%d" % (self.name, self.slot)

    def __hash__(self):
        return hash(self.name)


class MapWriteTerm(Cell):
    def __init__(self, assignments=None):
        Cell.__init__(self)
        self.assignments = assignments if assignments else {}

    def walk(self, visitor, accumulator=None):
        result = None
        for a in self.assignments:
            result = visitor(a, accumulator)  # TODO store assignment keys as VarTerms
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


class MapReadTerm(Cell):
    def __init__(self, map, key):
        Cell.__init__(self)
        self.map = map  # the map name
        self.key = key  # the key to retrieve from it

    def walk(self, visitor, accumulator=None):
        return visitor(self.map, accumulator) or visitor(self.key, accumulator)

    def to_string(self):
        return "%s[%s]" % (self.map, self.key)
