from src.meta.term import VarTerm, ListPatternTerm, ListTerm, ApplTerm


class ContextError(Exception):
    def __init__(self, reason):
        self.reason = reason


class Context:
    def __init__(self):
        self.map = {}

    def bind(self, pattern, term):
        """Bind the names free variables in a pattern to values in a term and save them in a context; TODO make this
        non-static?"""
        if isinstance(pattern, VarTerm):
            self.map[pattern.name] = term
        elif isinstance(pattern, ListPatternTerm):
            for i in range(len(pattern.vars)):
                self.map[pattern.vars[i].name] = term.items[i]
            rest = term.items[len(pattern.vars):]
            self.map[pattern.rest.name] = ListTerm(rest)
        elif isinstance(pattern, ApplTerm):
            if len(term.args) != len(pattern.args):
                raise ContextError("Expected the term and the pattern to have the same number of arguments")
            for i in range(len(term.args)):
                self.bind(pattern.args[i], term.args[i])

    def resolve(self, term):
        """Using a context, resolve the names of free variables in a pattern to create a new term"""
        if isinstance(term, VarTerm) and term.name in self.map:
            return self.map[term.name]
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

    def __str__(self):
        return str(self.map)
