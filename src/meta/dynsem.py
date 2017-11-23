from src.meta.term import VarTerm
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
        transform = "%s --> %s" % (self.before, self.after)
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
        return "%s --> [native function]" % self.before


class Premise(Printable):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, context, interpret):
        raise NotImplementedError()

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

    def evaluate(self, context, interpret):
        if self.right.matches(self.left):
            context.bind(self.left, self.right)
        else:
            raise DynsemError("Expected %s to match %s" % (self.left, self.right))

    def to_string(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class EqualityCheckPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def evaluate(self, context, interpret):
        # TODO interpret each side here
        left_term = context.resolve(self.left)
        right_term = context.resolve(self.right)
        if not left_term.equals(right_term):
            raise DynsemError("Expected %s to equal %s" % (self.left, self.right))

    def to_string(self):
        return "%s %s %s" % (self.left, "==", self.right)


class AssignmentPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def evaluate(self, context, interpret):
        if isinstance(self.left, VarTerm):
            context.bind(self.left, context.resolve(self.right))
        else:
            raise DynsemError("Cannot assign to anything other than a variable (e.g. x => 2); TODO add " +
                              "support for constructor assignment (e.g. a(1, 2) => a(x, y))")

    def to_string(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class ReductionPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def evaluate(self, context, interpret):
        intermediate_term = context.resolve(self.left)
        new_term = interpret(intermediate_term)
        context.bind(self.right, new_term)

    def to_string(self):
        return "%s %s %s" % (self.left, "-->", self.right)


class CasePremise(Premise):
    def __init__(self, left, values=None, premises=None):
        Premise.__init__(self, left, None)
        self.values = values if values else []
        self.premises = premises if premises else []

    def evaluate(self, context, interpret):
        value = context.resolve(self.left)
        found = None
        for i in range(len(self.values)):
            if self.values[i] is None:  # otherwise branch
                found = self.premises[i]
                break
            elif self.values[i].matches(value):
                found = self.premises[i]
                break
        if found:
            found.evaluate(context, interpret)
        if not found:
            raise DynsemError("Unable to find matching branch in case statement: %s" % str(self))

    def to_string(self):
        return "case %s of {...}" % self.left
