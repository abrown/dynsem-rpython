from src.meta.printable import Printable
from src.meta.term import VarTerm, ListPatternTerm, ListTerm, ApplTerm


class ContextError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Context(Printable):
    def __init__(self):
        self.bound_names = {}  # name to path mapping

    def bind(self, pattern, path=['term']):
        """Bind the names free variables in a pattern to values in a term and save them in a context"""
        if isinstance(pattern, VarTerm):
            self.bound_names[pattern.name] = path
        elif isinstance(pattern, ListTerm):
            # x, y and z in [x, y, z]
            for i in range(len(pattern.items)):
                subpath = list(path)
                subpath.append('items[%d]' % i)
                self.bind(pattern.items[i], subpath)
        elif isinstance(pattern, ListPatternTerm):
            # x and y in [x, y | zs]
            for i in range(len(pattern.vars)):
                subpath = list(path)
                subpath.append('items[%d]' % i)
                self.bound_names[pattern.vars[i].name] = subpath
            # zs in [x, y | zs]
            subpath = list(path)
            subpath.append('items[%d:]' % len(pattern.vars))
            self.bound_names[pattern.rest.name] = subpath
        elif isinstance(pattern, ApplTerm):
            # x and y in a(x, y)
            for i in range(len(pattern.args)):
                subpath = list(path)
                subpath.append('args[%d]' % i)
                self.bind(pattern.args[i], subpath)

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

    def __resolve_appl(self, term):
        resolved_args = []
        for arg in term.args:
            resolved_arg = self.resolve(arg)
            if isinstance(resolved_arg, ListTerm) and not resolved_arg.items:
                continue  # special case for empty lists; TODO should we dispose of empty lists like this?
            else:
                resolved_args.append(resolved_arg)
        return ApplTerm(term.name, resolved_args)

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
