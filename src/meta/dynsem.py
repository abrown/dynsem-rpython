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


class Transformation:
    def __init__(self, before):
        self.before = before

    def matches(self, term):
        return self.before.matches(term)

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


class Rule(Transformation):
    def __init__(self, before, after, components=None, premises=None):
        Transformation.__init__(self, before)
        self.after = after
        self.components = components if components else []
        self.premises = premises if premises else []

    def __str__(self):
        transform = "%s --> %s" % (self.before, self.after)
        if self.premises:
            transform += " where "
            transform += "; ".join(map(str, self.premises))
        return transform


class NativeFunction(Transformation):
    def __init__(self, before, action):
        Transformation.__init__(self, before)
        self.action = action

    def __str__(self):
        return "%s --> [native function]" % self.before


class Premise:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return "%s %s %s" % (self.left, "?", self.right)

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


class PatternMatchPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def __str__(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class EqualityCheckPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def __str__(self):
        return "%s %s %s" % (self.left, "==", self.right)


class AssignmentPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def __str__(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class ReductionPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def __str__(self):
        return "%s %s %s" % (self.left, "-->", self.right)


class CasePremise(Premise):
    def __init__(self, left, values=None, premises=None):
        Premise.__init__(self, left, None)
        self.values = values if values else []
        self.premises = premises if premises else []

    def __str__(self):
        return "case %s of {...}" % self.left
