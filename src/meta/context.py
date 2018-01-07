from src.meta.printable import Printable
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


class Context(Printable):
    _immutable_ = True

    def __init__(self, appl_term, number_of_bound_terms):
        if appl_term.bound_terms is None:
            appl_term.bound_terms = [None] * number_of_bound_terms
        self.bound_terms = appl_term.bound_terms

    @unroll_safe
    def bind(self, pattern, term):
        """Bind the names free variables in a pattern to values in a term and save them in a context"""
        if isinstance(pattern, VarTerm):
            self.bound_terms[pattern.slot] = term
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
            assert self.bound_terms[term.slot] is not None
            return self.bound_terms[term.slot]
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
        return ApplTerm(term.name, resolved_args, term.trans, term.bound_terms)

    @unroll_safe
    def __resolve_list(self, term):
        resolved_items = []
        for i in range(len(term.items)):
            resolved_items.append(self.resolve(term.items[i]))
        return ListTerm(resolved_items)

    def to_string(self):
        terms = []
        for bt in self.bound_terms:
            if bt is None:
                terms.append("None")
            else:
                terms.append(bt.to_string())
        return "[%s]" % (", ".join(terms))
