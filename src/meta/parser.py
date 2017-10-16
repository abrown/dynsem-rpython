from .dynsem import *
from .term import *
from .tokenizer import *


class ParseError(Exception):
    def __init__(self, reason, token):
        self.reason = reason
        self.token = token


class Parser:
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
        self.module = Module()

    @staticmethod
    def term(text):
        """Helper method for parsing a single term"""
        return Parser(text).__parse_term()

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
                    before = self.__parse_term()
                    if before is None: break;
                    self.__expect_value(OperatorToken, "-->")
                    after = self.__expect_term()
                    rule = Rule(before, after)
                    if self.__possible_value(KeywordToken, "where"):
                        while True:
                            premise = self.__parse_premise()
                            rule.premises.append(premise)
                            if not self.__possible(SemiColonToken): break
                        self.__expect(PeriodToken)
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
            raise ParseError("Expected a token of {} but found: ".format(type), token)
        return token

    def __expect_value(self, type, expected=None):
        token = self.__expect(type)
        if expected and token.value != expected:
            raise ParseError("Expected a token with value {} but found: ".format(expected), token.value)

    def __possible(self, type):
        token = self.tokenizer.next()
        if isinstance(token, type):
            return token
        else:
            self.tokenizer.undo(token)
            return None

    def __possible_value(self, type, expected):
        token = self.__possible(type)
        return token if token and expected and token.value is not expected else None

    def __parse_term(self):
        token = self.tokenizer.next()
        if isinstance(token, IdToken):
            return self.__parse_identifier(token)
        elif isinstance(token, NumberToken):
            return IntTerm(token.value)
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
        else:
            return VarTerm(id.value)

    def __expect_term(self):
        term = self.__parse_term()
        if term is None:
            raise ParseError("Failed to parse a term", None)
        return term

    def __parse_premise(self):
        left = self.__parse_term()
        operator = self.__expect(OperatorToken)
        right = self.__parse_term()

        if "==" == operator.value:
            return EqualityCheckPremise(left, right)
        elif "=>" == operator.value:
            return PatternMatchPremise(left, right)
        else:
            raise NotImplementedError()
