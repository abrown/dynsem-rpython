from src.meta.dynsem import *
from src.meta.term import *
from src.meta.tokenizer import *


class ParseError(Exception):
    def __init__(self, reason, token):
        self.reason = reason
        self.token = token

    def __str__(self):
        return self.reason + " at token " + str(self.token)


class Parser:
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
        self.module = Module()

    @staticmethod
    def term(text):
        """Helper method for parsing a single term"""
        return Parser(text).__parse_term()

    @staticmethod
    def rule(text):
        """Helper method for parsing a single rule"""
        return Parser(text).__parse_rule()

    @staticmethod
    def premise(text):
        """Helper method for parsing a single premise"""
        return Parser(text).__parse_premise()

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
                    if self.__possible(KeywordToken) or self.__possible(EofToken): break
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
            if last is None: break
        return self.module

    def __collect(self, type):
        tokens = []
        while True:
            token = self.tokenizer.next()
            if not isinstance(token, type):
                self.tokenizer.undo(token)
                break
            tokens.append(token)
        return tokens

    def __expect(self, type):
        token = self.tokenizer.next()
        if not isinstance(token, type):
            raise ParseError("Expected a token of %s but found: " % type, token)
        return token

    def __expect_value(self, type, expected=None):
        token = self.__expect(type)
        if expected and token.value != expected:
            raise ParseError("Expected a token with value %s but found: " % str(expected), token)

    def __possible(self, type):
        token = self.tokenizer.next()
        if isinstance(token, type):
            return token
        else:
            self.tokenizer.undo(token)
            return None

    def __possible_value(self, type, expected):
        token = self.tokenizer.next()
        if isinstance(token, type) and expected and token.value == expected:
            return token
        else:
            self.tokenizer.undo(token)
            return None

    def __parse_term(self):
        token = self.tokenizer.next()
        if isinstance(token, IdToken):
            return self.__parse_identifier(token)
        elif isinstance(token, NumberToken):
            return IntTerm(0 if token.value is None else int(token.value))
        elif isinstance(token, LeftBraceToken):
            return self.__parse_new_environment(token)
        else:
            self.tokenizer.undo(token)
            return None

    def __parse_identifier(self, id):
        if self.__possible(LeftParensToken):
            args = []
            while True:
                arg = self.__parse_term()
                if arg is None: break
                args.append(arg)
                self.__possible(CommaToken)
            self.__expect(RightParensToken)
            return ApplTerm(id.value, args)
        if self.__possible(LeftBracketToken):
            name = self.__expect(IdToken)
            self.__expect(RightBracketToken)
            return EnvReadTerm(id.value, name.value)
        else:
            return VarTerm(id.value)

    def __parse_new_environment(self, id):
        assignments = {}
        while True:
            name = self.__parse_term()
            if name is None: break
            if not isinstance(name, VarTerm): raise ParseError("Expected a variable term but found " + str(name), None)
            if self.__possible_value(OperatorToken, "|-->"):
                value = self.__expect_term()
            else:
                value = EnvWriteTerm()  # TODO this is by "convention" but not necessarily clear
            assignments[name.name] = value
            self.__possible(CommaToken)
        self.__expect(RightBraceToken)
        return EnvWriteTerm(assignments)

    def __expect_term(self):
        term = self.__parse_term()
        if term is None:
            raise ParseError("Expected to parse a term", self.tokenizer.next())
        return term

    def __parse_premise(self):
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
                if not self.__possible(SemiColonToken): break
            self.__possible(PeriodToken)

        return Rule(before, after, components, premises)
