from .term import *


class Module:
    name = ""
    imports = []
    sorts = []
    constructors = []
    arrows = []
    components = []
    nativeOperators = []
    rules = []


class Rule:
    def __init__(self, before, after, premises=None):
        if premises is None:
            premises = []
        self.premises = premises
        self.before = before
        self.after = after


class Premise:
    def __init__(self, left, right):
        self.left = left
        self.right = right

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


class EqualityCheckPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)


class AssignmentPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)