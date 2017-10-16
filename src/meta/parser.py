from .tokenizer import *
from .dynsem import *


class ParseError(Exception):
    def __init__(self, reason, token):
        self.reason = reason
        self.token = token


class Parser:
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
        self.module = Module()

    def parse_next(self):
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
                    before = self.parse_term()
                    if before is None: break;
                    self.__expect_value(OperatorToken, "-->")
                    after = self.__expect_term()
                    rule = Rule(before, after)
                    if self.__possible_value(KeywordToken, "where"):
                        while True:
                            premise = self.__attempt_premise()
                            if premise is None: break;
                            rule.premises.append(premise)
                    self.module.rules.append(rule)
            return self.module
        elif isinstance(token, EofToken):
            return None
        else:
            raise ParseError("Unexpected token", token)

    def parse_all(self):
        """Parse all tokens into a Module and return it"""
        while True:
            last = self.parse_next()
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


        # # Parse variable
        # def parse_var(tokens):
        #     tok = tokens.next()
        #     if (tok.ttype == ID):
        #         return tok.s
        #     else:
        #         raise ParseError('Missing variable name', tok.lineno)
        #
        # # Parse expression
        # def parse_exp(tokens):
        #     result = None
        #     tok = tokens.next()
        #     if tok.ttype == NUM:
        #         result = IntExp(tok.num)
        #     elif tok.ttype == ID:
        #         result = VarExp(tok.s)
        #     elif tok.ttype == LP:
        #         tok = tokens.next()
        #         if tok.ttype == ID:
        #             keywd = tok.s
        #             if keywd == "while":
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 result = WhileExp(e1, e2)
        #             elif keywd == "for":
        #                 x = parse_var(tokens)
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 e3 = parse_exp(tokens)
        #                 raise ParseError('Unsupported expression', tok.lineno) # change this!!
        #             elif keywd == "if":
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 e3 = parse_exp(tokens)
        #                 result = IfExp(e1, e2, e3)
        #             elif keywd == "write":
        #                 e = parse_exp(tokens)
        #                 result = WriteExp(e)
        #             elif keywd == "block": # convert to nested seq's on the fly
        #                 es = []
        #                 tok = tokens.next()
        #                 while (tok.ttype != RP):
        #                     tokens.putback(tok)
        #                     es.append(parse_exp(tokens))
        #                     tok = tokens.next()
        #                 tokens.putback(tok)
        #                 if len(es) == 0:
        #                     es = [IntExp(0)]
        #                 result = es[0]
        #                 for e in es[1:]:
        #                     result = SeqExp(result,e)
        #         elif tok.ttype == OPER:
        #             oper = tok.oper
        #             if oper == ":=":
        #                 v = parse_var(tokens)
        #                 e = parse_exp(tokens)
        #                 result = AsgnExp(v,e)
        #             elif oper == "+":
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 result = AddExp(e1, e2)
        #             elif oper == "-":
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 result = SubExp(e1, e2)
        #             elif oper == "*":
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 result = MulExp(e1, e2)
        #             elif oper == "/":
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 result = DivExp(e1, e2)
        #             elif oper == "<=":
        #                 e1 = parse_exp(tokens)
        #                 e2 = parse_exp(tokens)
        #                 result = LeqExp(e1, e2)
        #             else:
        #                 raise ParseError("Invalid operator:" + oper, tok.lineno)
        #         else:
        #             raise ParseError("Missing or invalid expression", tok.lineno)
        #         tok = tokens.next()
        #         if tok.ttype != RP:
        #             raise ParseError("Missing )", tok.lineno)
        #     else:
        #         raise ParseError("Missing or invalid expression", tok.lineno)
        #     return result
        #
        # # Parse program
        # def parse(text):
        #     tokens = Tokenizer(text)
        #     exp = parse_exp(tokens)
        #     tok = tokens.next()
        #     if tok.ttype != EOF:
        #         raise ParseError("Extraneous characters at end of program", tok.lineno)
        #     return exp

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

    def parse_term(self):
        token = self.tokenizer.next()
        if isinstance(token, IdToken):
            return self.__parse_appl(token)
        elif isinstance(token, NumberToken):
            return IntTerm(token.value)
        else:
            self.tokenizer.undo(token)
            return None

    def __parse_appl(self, id):
        args = []
        if not self.__possible(LeftParensToken) is None:
            while True:
                arg = self.parse_term()
                if arg is None: break
                args.append(arg)
                self.__possible(CommaToken)
            self.__expect(RightParensToken)
        return ApplTerm(id.value, args)

    def __expect_term(self):
        term = self.parse_term()
        if term is None:
            raise ParseError("Failed to parse a term", None)
        return term

    def __attempt_premise(self):
        pass
