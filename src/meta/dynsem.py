from context import Context
from src.meta.term import VarTerm, IntTerm


class DynsemError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Module:
    def __init__(self):
        self.name = ""
        self.imports = []
        self.sorts = []
        self.constructors = {}
        self.arrows = []
        self.components = []
        self.native_functions = []
        self.rules = []


class Constructor:
    def __init__(self, name, sorts=None, rules=None):
        self.name = name
        self.sorts = sorts if sorts else []
        self.rules = rules if rules else []


class Transformation:
    def to_string(self):
        return self.__str__()

    def matches(self, term):
        return self.before.matches(term)

    def transform(self, term, interpret):
        raise NotImplementedError

    def __init__(self, before):
        self.before = before

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

    def transform(self, term, interpret):
        context = Context()
        context.bind(self.before, term)

        # handle premises
        if self.premises:
            for premise in self.premises:
                premise.evaluate(context, interpret)

        result = context.resolve(self.after)
        return result

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

    def transform(self, term, interpret):
        context = Context()
        context.bind(self.before, term)

        args = []
        for arg in self.before.args:
            resolved = context.resolve(arg)
            interpreted = interpret(resolved)  # TODO need to determine what type of term to use, not hard-code this
            if not isinstance(interpreted, IntTerm): raise DynsemError("Expected parameter %s of %s to resolve to an IntTerm but was: %s" % (resolved, native_function, interpreted))
            args.append(interpreted.number)

        if(len(args) < 2): args.append(0)
        tuple_args = (args[0], args[1])  # TODO RPython demands this

        result = self.action(*tuple_args)
        return IntTerm(result)  # TODO need to determine what type of term to use, not hard-code this

    def __str__(self):
        return "%s --> [native function]" % self.before


class Premise:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, context, interpret):
        raise NotImplementedError()

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

    def evaluate(self, context, interpret):
        if self.right.matches(self.left):
            context.bind(self.left, self.right)
        else:
            raise DynsemError("Expected %s to match %s" % (self.left, self.right))

    def __str__(self):
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

    def __str__(self):
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

    def __str__(self):
        return "%s %s %s" % (self.left, "=>", self.right)


class ReductionPremise(Premise):
    def __init__(self, left, right):
        Premise.__init__(self, left, right)

    def evaluate(self, context, interpret):
        intermediate_term = context.resolve(self.left)
        new_term = interpret(intermediate_term)
        context.bind(self.right, new_term)

    def __str__(self):
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

    def __str__(self):
        return "case %s of {...}" % self.left
