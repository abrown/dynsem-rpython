from src.meta.dynsem import *
from src.meta.slot_assigner import SlotAssigner
from src.meta.term import *
from src.meta.tokenizer import *


class ParseError(Exception):
    def __init__(self, reason, token):
        self.reason = reason
        self.token = token

    def __str__(self):
        return self.reason + " at token " + str(self.token)


class PlaceholderCell(Cell):
    pass


class TermCollector:
    def __init__(self):
        self.cells = []
        self.var_terms = []
        self.offset = 0

    def add_cell(self, cell):
        assert cell is not None
        self.cells.append(cell)
        previous_offset = self.offset
        self.offset += 1
        return previous_offset

    def add_variable_cell(self, cell):
        assert cell is not None and isinstance(cell, VarTerm)
        self.cells.append(cell)
        self.var_terms.append(self.offset)
        previous_offset = self.offset
        self.offset += 1
        return previous_offset

    def visit(self, visitor, start=0, end=-1):
        end = end if end > -1 else self.offset
        for i in range(start, end):
            visitor(self.cells[i])


class FlatParser:
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
        self.module = Module()

    @staticmethod
    def term(text):
        """Helper method for parsing a single term"""
        collector = TermCollector()
        number_of_subterms = FlatParser(text).__parse_term(collector)
        return Term(collector.cells, collector.var_terms) if number_of_subterms else None

    # @staticmethod
    # def native_function(text):
    #     """Helper method for parsing a single term; has slot assignment for native contexts"""
    #     term = Parser(text).__parse_term()
    #     assigned = SlotAssigner().assign_term(term)
    #     if assigned != 2:
    #         print("Expected native function to have two terms assigned: " + term.to_string())
    #     return term

    # @staticmethod
    # def rule(text):
    #     """Helper method for parsing a single rule"""
    #     rule = Parser(text).__parse_rule()
    #     return rule

    # @staticmethod
    # def premise(text):
    #     """Helper method for parsing a single premise"""
    #     return Parser(text).__parse_premise()

    def next(self):
        """Parse one token and update the Module"""
        token = self.tokenizer.next()
        if isinstance(token, KeywordToken):
            keyword = token.value
            if keyword == "module":
                self.module.name = self.__expect(IdToken).value
            elif keyword == "imports":
                self.module.imports = [t.value for t in self.__collect(IdToken)]
            elif keyword == "rules":
                while True:
                    if self.__possible(KeywordToken) or self.__possible(EofToken):
                        break
                    rule = self.__parse_rule()
                    self.module.rules.append(rule)
            return self.module
        elif isinstance(token, EofToken):
            return None
        else:
            raise ParseError("Unexpected token", token)

    def all(self):
        """Parse all tokens into a Module and return it"""
        while True:
            last = self.next()
            if last is None:
                break
        return self.module

    def __collect(self, token_type):
        tokens = []
        while True:
            token = self.tokenizer.next()
            if not isinstance(token, token_type):
                self.tokenizer.undo(token)
                break
            tokens.append(token)
        return tokens

    def __expect(self, token_type):
        token = self.tokenizer.next()
        if not isinstance(token, token_type):
            raise ParseError("Expected a token of %s but found something else" % token_type, token)
        return token

    def __expect_value(self, token_type, expected=None):
        token = self.__expect(token_type)
        if expected and token.value != expected:
            raise ParseError("Expected a token with value %s but found something else" % str(expected), token)

    def __possible(self, token_type):
        token = self.tokenizer.next()
        if isinstance(token, token_type):
            return token
        else:
            self.tokenizer.undo(token)
            return None

    def __possible_value(self, token_type, expected):
        token = self.tokenizer.next()
        if isinstance(token, token_type) and expected and token.value == expected:
            return token
        else:
            self.tokenizer.undo(token)
            return None

    def __parse_term(self, collector):
        start_offset = collector.offset
        token = self.tokenizer.next()
        if isinstance(token, IdToken):
            self.__parse_identifier(token, collector)
        elif isinstance(token, NumberToken):
            cell = IntTerm(0 if token.value is None else int(token.value))
            collector.add_cell(cell)
        elif isinstance(token, LeftBraceToken):
            self.__parse_new_environment(token)
        elif isinstance(token, LeftBracketToken):
            self.__parse_list(token, collector)
        else:
            self.tokenizer.undo(token)
        end_offset = collector.offset
        return end_offset - start_offset

    def __parse_identifier(self, id_token, collector):
        if self.__possible(LeftParensToken):
            self.__parse_appl(id_token, collector)
        elif self.__possible(LeftBracketToken):
            name = self.__expect(IdToken)
            self.__expect(RightBracketToken)
            return MapReadTerm(VarTerm(id_token.value), VarTerm(name.value))
        else:
            collector.add_variable_cell(VarTerm(id_token.value))

    def __parse_appl(self, id_token, collector):
        appl_term = ApplTerm(id_token.value)
        collector.add_cell(appl_term)
        start_offset = collector.offset
        while True:
            number_of_subterms = self.__parse_term(collector)
            if number_of_subterms < 1:
                break
            self.__possible(CommaToken)
        self.__expect(RightParensToken)
        end_offset = collector.offset
        appl_term.size = end_offset - start_offset

    def __parse_list(self, token, collector):
        start_offset = collector.add_cell(PlaceholderCell())

        # normal list
        while True:
            number_of_subterms = self.__parse_term(collector)
            if number_of_subterms < 1:
                break
            if not self.__possible(CommaToken):
                break

        # list pattern
        if self.__possible_value(OperatorToken, "|"):
            def assert_var_term(t):
                if not isinstance(t, VarTerm):
                    raise ParseError("Expected list pattern to only include VarTerms", token)

            # parse the 'tail' term (e.g. [head | tail])
            self.__expect_term()

            # assert all terms are VarTerms (e.g. [x1, x2, x3 | xs])
            collector.visit(assert_var_term, collector.offset)

            replacement_cell = ListPatternTerm(collector.offset - start_offset, collector.offset)
        else:
            replacement_cell = ListTerm(collector.offset - start_offset)

        self.__expect(RightBracketToken)

        # replace the placeholder
        collector.cells[start_offset] = replacement_cell

    def __parse_new_environment(self, token):
        assignments = {}
        while True:
            name = self.__parse_term()
            if name is None:
                break
            if not isinstance(name, VarTerm):
                raise ParseError("Expected a variable term but found " + str(name), None)
            if self.__possible_value(OperatorToken, "|-->"):
                value = self.__expect_term()
            else:
                value = MapWriteTerm()  # TODO this is by "convention" but not necessarily clear
            assignments[name] = value
            self.__possible(CommaToken)
        self.__expect(RightBraceToken)
        return MapWriteTerm(assignments)

    def __expect_term(self):
        term = self.__parse_term()
        if term is None:
            raise ParseError("Expected to parse a term", self.tokenizer.next())
        return term

    def __parse_premise(self):
        if self.__possible_value(KeywordToken, "case"):
            return self.__parse_case()

        left = self.__parse_term()
        operator = self.__expect(OperatorToken)
        right = self.__parse_term()

        if "==" == operator.value:
            return EqualityCheckPremise(left, right)
        elif "=>" == operator.value:
            if isinstance(right, ApplTerm):
                return PatternMatchPremise(left, right)
            else:
                return AssignmentPremise(left, right)
        elif "-->" == operator.value:
            return ReductionPremise(left, right)
        else:
            raise NotImplementedError()

    def __parse_case(self):
        var = self.__expect_term()
        self.__expect_value(KeywordToken, "of")
        self.__expect(LeftBraceToken)

        values = []
        sub_premises = []
        while True:
            if self.__possible_value(KeywordToken, "otherwise"):
                values.append(None)
            else:
                values.append(self.__expect_term())
            self.__expect_value(OperatorToken, "=>")
            sub_premises.append(self.__parse_premise())
            if self.__possible(RightBraceToken):
                break

        return CasePremise(var, values, sub_premises)

    def __parse_rule(self):
        before = self.__expect_term()

        # parse semantic components
        components = []
        if self.__possible_value(OperatorToken, "|-"):
            components.append(before)
            before = self.__expect_term()

        # read body
        self.__expect_value(OperatorToken, "-->")
        after = self.__expect_term()

        # parse premises
        premises = []
        if self.__possible_value(KeywordToken, "where"):
            while True:
                premise = self.__parse_premise()
                premises.append(premise)
                if not self.__possible(SemiColonToken):
                    break
            self.__possible(PeriodToken)

        # assign slot numbers
        number_of_bound_terms = SlotAssigner().assign_rule(before, after, premises)

        return Rule(before, after, components, premises, number_of_bound_terms)
