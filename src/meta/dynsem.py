class Module:
    def __init__(self):
        self.name = ""
        self.imports = []
        self.sorts = []
        self.constructors = []
        self.arrows = []
        self.components = []
        self.nativeOperators = []
        self.rules = []


class Rule:
    def __init__(self, before, after, premises=None):
        if premises is None:
            premises = []
        self.premises = premises
        self.before = before
        self.after = after

    def __str__(self):
        transform = "{} --> {}".format(self.before, self.after)
        if self.premises:
            transform += " where "
            transform += "; ".join(map(str, self.premises))
        return transform

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented
        # if not isinstance(other, self.__class__): return False
        # return self.before == other.before and self.after == other.after and self.premises == other.premises

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented


class Premise:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return "{} {} {}".format(self.left, "?", self.right)

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
        return "{} {} {}".format(self.left, "=>", self.right)


class EqualityCheckPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def __str__(self):
        return "{} {} {}".format(self.left, "==", self.right)


class AssignmentPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def __str__(self):
        return "{} {} {}".format(self.left, "=>", self.right)