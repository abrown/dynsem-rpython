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

    def to_joining_string(self, string, start, end):
        for cursor in range(start, end):
            string += self.to_string_from_cell(cursor)
            string += ", "

    def to_assignment_joining_string(self, string, start, end):
        for cursor in range(start, end):
            string += self.to_string_from_cell(string, cursor)
            string += " --> "
            string += self.to_string_from_cell(string, cursor)
            string += ", "
            # TODO handle single varterms

    def to_string_from_cell(self, string, cursor):
        cell = self.cells[cursor]
        if isinstance(cell, ApplTerm):
            string += cell.to_string() + "("
            string += self.to_joining_string(string, cursor, cursor + cell.size)
            string += ")"
        elif isinstance(cell, ListTerm):
            string += "["
            string += self.to_joining_string(string, cursor, cursor + cell.size)
            string += "]"
        elif isinstance(cell, ListPatternTerm):
            string += "["
            string += self.to_joining_string(string, cursor, cursor + cell.size - 1)
            string += ("| %s ]" % self.cells[cell.tail_offset].to_string())
        elif isinstance(cell, MapReadTerm):
            string += cell.to_string() + "["
            string += self.to_string_from_cell(string, cursor + 1)
            string += "]"
        elif isinstance(cell, MapWriteTerm):
            string += "{"
            string += self.to_joining_string(string, cursor, cursor + cell.size - 1)
            string += "}"
        else:
            string += cell.to_string()
        return string

    def to_string(self):
        return self.to_string_from_cell("", 0)


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
    def __init__(self, name, size=0, end_offset=0, trans=None, bound_terms=None):
        Cell.__init__(self)
        self.name = name
        self.size = size
        self.end_offset = end_offset
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
    def __init__(self, size=0, end_offset=0):
        Cell.__init__(self)
        self.size = size
        self.end_offset = end_offset

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


class ListPatternTerm(ListTerm):
    pass


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
    def __init__(self, size=0, end_offset=0):
        Cell.__init__(self)
        self.size = size
        self.end_offset = end_offset

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


class AssignmentTerm(Cell):
    def __init__(self, end_offset):
        Cell.__init__(self)
        self.end_offset = end_offset


class MapReadTerm(Cell):
    def __init__(self, end_offset=0):
        Cell.__init__(self)
        self.end_offset = end_offset

    def walk(self, visitor, accumulator=None):
        return visitor(self.map, accumulator) or visitor(self.key, accumulator)

