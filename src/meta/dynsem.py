from src.meta.printable import Printable


class DynsemError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Module:
    def __init__(self):
        self.name = ""
        self.imports = []
        self.sorts = []
        self.constructors = []
        self.arrows = []
        self.components = []
        self.native_functions = []
        self.rules = []


class Transformation(Printable):
    def __init__(self, before):
        self.before = before

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
    def __init__(self, before, after, components=None, premises=None):
        Transformation.__init__(self, before)
        self.after = after
        self.components = components if components else []
        self.premises = premises if premises else []

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
    def __init__(self, before, action):
        Transformation.__init__(self, before)
        self.action = action

    def to_string(self):
        return "%s --> [native function]" % self.before.to_string()


class Premise(Printable):
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
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class EqualityCheckPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "==", self.right)


class AssignmentPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class ReductionPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def to_string(self):
        return "%s %s %s" % (self.left, "-->", self.right)


class CasePremise(Premise):
    def __init__(self, left, values=None, premises=None):
        Premise.__init__(self, left, None)
        self.values = values if values else []
        self.premises = premises if premises else []

    def to_string(self):
        return "case %s of {...}" % self.left
