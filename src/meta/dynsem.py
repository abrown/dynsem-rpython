from src.meta.printable import Printable

try:
    from rpython.rlib.jit import hint
except ImportError:
    def hint(x, **kwds):
        return x


class DynsemError(Exception):
    def __init__(self, reason):
        self.reason = reason


class ModuleBuilder:
    def __init__(self):
        self.name = ""
        self.imports = []
        self.sorts = []
        self.constructors = []
        self.arrows = []
        self.components = []
        self.native_functions = []
        self.rules = []


class Module:
    _immutable_fields_ = ['rules[*]', 'native_functions[*]']

    def __init__(self, rules=None, native_functions=None):
        self.rules = rules if rules else []
        self.native_functions = native_functions if native_functions else []


class Transformation(Printable):
    _immutable_fields_ = ['before', 'bound_terms']

    def __init__(self, before, number_of_bound_terms=0):
        self.before = before
        self.bound_terms = [None] * number_of_bound_terms

    def matches(self, term):
        return self.before.matches(term)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class Rule(Transformation):
    _immutable_fields_ = ['before', 'after', 'components[*]', 'premises[*]']

    def __init__(self, before, after, components=None, premises=None, number_of_bound_terms=0, has_loop=False):
        Transformation.__init__(self, before, number_of_bound_terms)
        self.after = after
        self.components = components if components else []
        self.premises = premises if premises else []
        self.has_loop = has_loop

    def to_string(self):
        transform = "%s --> %s" % (self.before.to_string(), self.after.to_string())
        if self.premises:
            premises = []
            for premise in self.premises:
                premises.append(premise.to_string())
            transform += " where "
            transform += "; ".join(premises)
        return transform


class NativeFunction(Transformation):
    _immutable_fields_ = ['before', 'action']

    def __init__(self, before, action, number_of_bound_terms=2):
        Transformation.__init__(self, before, number_of_bound_terms)
        self.action = action

    def to_string(self):
        return "%s --> [native function]" % self.before.to_string()


class Premise(Printable):
    _immutable_fields_ = ['left', 'right']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_string(self):
        return "%s %s %s" % (self.left, "?", self.right)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class PatternMatchPremise(Premise):
    _immutable_fields_ = ['left', 'right']

    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class EqualityCheckPremise(Premise):
    _immutable_fields_ = ['left', 'right']

    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "==", self.right)


class AssignmentPremise(Premise):
    # TODO remove, same as pattern match
    _immutable_fields_ = ['left', 'right']

    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class ReductionPremise(Premise):
    _immutable_fields_ = ['left', 'right']

    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "-->", self.right)


class CasePremise(Premise):
    _immutable_fields_ = ['left', 'values[*]', 'premises[*]']

    def __init__(self, left, values=None, premises=None):
        Premise.__init__(self, left, None)
        self.values = values if values else []
        self.premises = premises if premises else []

    def to_string(self):
        subpremises = []
        for i in range(len(self.values)):
            left = self.values[i].to_string() if self.values[i] else "otherwise"
            right = self.premises[i].to_string()
            sp = "%s => %s" % (left, right)
            subpremises.append(sp)
        return "case %s of {%s}" % (self.left, "; ".join(subpremises))
