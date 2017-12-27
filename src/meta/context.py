from src.meta.dynsem import PatternMatchPremise, EqualityCheckPremise, ReductionPremise, CasePremise, AssignmentPremise
from src.meta.term import VarTerm, ListPatternTerm, ListTerm, ApplTerm

# So that you can still run this module under standard CPython...
try:
    from rpython.rlib.jit import unroll_safe, hint
except ImportError:
    def hint(x, **kwds):
        return x


    def unroll_safe(func):
        return func


class ContextError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Context:
    _immutable_fields_ = ['map']

    # TODO should this be the default size
    def __init__(self, size):
        self = hint(self, access_directly=True, fresh_virtualizable=True)
        if size is None:
            raise ValueError("Expected context to be instantiated with a size")
        self.map = [None] * size
        # TODO generate this array on rules and make it static, no need to create each time

    @unroll_safe
    def bind(self, pattern, term):
        """Bind the names free variables in a pattern to values in a term and save them in a context; TODO make this
        non-static?"""
        if isinstance(pattern, VarTerm):
            self.map[pattern.slot] = term
        elif isinstance(pattern, ListTerm):
            if not isinstance(term, ListTerm):
                raise ContextError("Expected the term to be a list but was: " + term.to_string())
            if len(term.items) != len(pattern.items):
                raise ContextError("Expected the term and the pattern to have the same number of items")
            for i in range(len(pattern.items)):
                self.bind(pattern.items[i], term.items[i])
        elif isinstance(pattern, ListPatternTerm):
            if not isinstance(term, ListTerm):
                raise ContextError("Expected the term to be a list but was: " + term.to_string())
            for i in range(len(pattern.vars)):
                self.bind(pattern.vars[i], term.items[i])
            rest = term.items[len(pattern.vars):]
            self.bind(pattern.rest, ListTerm(rest))
        elif isinstance(pattern, ApplTerm):
            if not isinstance(term, ApplTerm):
                raise ContextError("Expected the term to both be an application but was: " + term.to_string())
            if len(term.args) != len(pattern.args):
                raise ContextError("Expected the term and the pattern to have the same number of arguments")
            for i in range(len(term.args)):
                self.bind(pattern.args[i], term.args[i])

    @unroll_safe
    def resolve(self, term):
        """Using a context, resolve the names of free variables in a pattern to create a new term"""
        if isinstance(term, VarTerm) and term.slot >= 0:
            return self.map[term.slot]
        elif isinstance(term, ApplTerm):
            return self.__resolve_appl(term)
        elif isinstance(term, ListTerm):
            return self.__resolve_list(term)
        else:
            return term

    @unroll_safe
    def __resolve_appl(self, term):
        resolved_args = []
        for arg in term.args:
            resolved_arg = self.resolve(arg)
            if isinstance(resolved_arg, ListTerm) and not resolved_arg.items:
                continue  # special case for empty lists; TODO should we dispose of empty lists like this?
            else:
                resolved_args.append(resolved_arg)
        return ApplTerm(term.name, resolved_args, term.trans)

    @unroll_safe
    def __resolve_list(self, term):
        resolved_items = []
        for i in range(len(term.items)):
            resolved_items.append(self.resolve(term.items[i]))
        return ListTerm(resolved_items)

    def __str__(self):
        return str(self.map)


class SlotAssigner:
    def __init__(self):
        self.mapping = {}
        self.slot = 0

    def assign_rule(self, rule):
        if rule is None:
            raise ValueError("Expected a rule, not none")

        slot_before = self.slot
        self.__bound(rule.before)
        for premise in rule.premises:
            self.assign_premise(premise)
        self.__resolved(rule.after)

        return self.slot - slot_before

    def assign_premise(self, premise):
        if premise is None:
            raise ValueError("Expected a premise, not none")

        slot_before = self.slot
        if isinstance(premise, PatternMatchPremise):
            self.__bound(premise.left)
            self.__resolved(premise.right)
        if isinstance(premise, AssignmentPremise):  # TODO remove
            self.__bound(premise.left)
            self.__resolved(premise.right)
        elif isinstance(premise, EqualityCheckPremise):
            self.__resolved(premise.left)
            self.__resolved(premise.right)
        elif isinstance(premise, ReductionPremise):
            self.__resolved(premise.left)
            self.__bound(premise.right)
        elif isinstance(premise, CasePremise):
            self.__resolved(premise.left)
            for subpremise in premise.premises:
                self.assign_premise(subpremise)
        else:
            raise NotImplementedError("Unknown premise type: " + premise.__class__.__name__)

        return self.slot - slot_before

    def __bound(self, term):
        if term is None:
            raise ValueError("Expected a term, not none")

        def set_as_bound(term, assigner):
            if isinstance(term, VarTerm):
                if term.name in assigner.mapping:
                    term.slot = assigner.mapping[term.name]
                else:
                    assigner.mapping[term.name] = assigner.slot
                    term.slot = assigner.slot
                    assigner.slot += 1

        term.walk(set_as_bound, self)

    def __resolved(self, term):
        if term is None:
            raise ValueError("Expected a term, not none")

        def set_as_resolved(term, assigner):
            if isinstance(term, VarTerm):
                if term.name in assigner.mapping:
                    term.slot = assigner.mapping[term.name]
                else:
                    pass
                    # TODO print warning re: unresolvable var term

        term.walk(set_as_resolved, self)

    def assign_term(self, term):
        before_slot = self.slot
        self.__bound(term)
        return self.slot - before_slot

        # if isinstance(term, VarTerm):
        #     term.slot = slot
        #     return slot + 1
        # elif isinstance(term, ApplTerm):
        #     for a in term.args:
        #         slot = SlotAssigner.assign_term(a, slot)
        #     return slot
        # elif isinstance(term, ListTerm):
        #     for i in term.items:
        #         slot = SlotAssigner.assign_term(i, slot)
        #     return slot
        # elif isinstance(term, ListPatternTerm):
        #     for v in term.vars:
        #         slot = SlotAssigner.assign_term(v, slot)
        #     slot = SlotAssigner.assign_term(term.rest, slot)
        #     return slot
        # elif isinstance(term, MapWriteTerm):
        #     raise NotImplementedError()
        # # TODO map terms
        # else:
        #     return slot
