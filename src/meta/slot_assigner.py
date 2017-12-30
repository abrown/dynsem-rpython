from src.meta.dynsem import PatternMatchPremise, EqualityCheckPremise, ReductionPremise, CasePremise, AssignmentPremise
from src.meta.term import Term, VarTerm


class SlotAssigner:
    def __init__(self):
        self.mapping = {}
        self.slot = 0

    def assign_rule(self, before, after, premises):
        if not isinstance(before, Term) or not isinstance(after, Term) or not isinstance(premises, list):
            raise ValueError("Expected before and after terms and a list of premises but was passed: %s, %s, %s" % (
            before, after, premises))

        slot_before = self.slot
        self.__bound(before)
        for premise in premises:
            self.assign_premise(premise)
        self.__resolved(after)

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
