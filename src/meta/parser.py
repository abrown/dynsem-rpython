from tokenizer import *

class Module:
    name = ""
    imports = []
    sorts = []
    constructors = []
    arrows = []
    components = []
    nativeOperators = []
    rules = []

class ParseError(Exception):
    def __init__(self, reason, token):
        self.reason = reason
        self.token = token

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.module = Module()

    def get(self, type):
        token = self.tokenizer.next()
        if not isinstance(token, type):
            raise ParseError("Expected a token of {} but found: ".format(type), token);
        return token

    def expect(self, type, expected=None):
        token = self.get(type)
        if expected and token.value is not expected:
            raise ParseError("Expected a token with value {} but found: ".format(expected), token.value);

    def parse(self):
        token = self.tokenizer.next()
        if isinstance(token, KeywordToken):
            keyword = token.value
            if keyword == "module"
                self.module.name = self.get(IdToken)
            elif keyword == "imports"
                path = self.get(IdToken)
                while isinstance(path, IdToken)
                    self.module.imports.append(path.value)
                    path = self.get(IdToken)
                self.tokenizer.back(path) # would prefer not to do this
            elif keyword == "constructors"


# Parse variable
def parse_var(tokens):
    tok = tokens.next()
    if (tok.ttype == ID):
        return tok.s
    else:
        raise ParseError('Missing variable name', tok.lineno)

# Parse expression
def parse_exp(tokens):
    result = None
    tok = tokens.next()
    if tok.ttype == NUM:
        result = IntExp(tok.num)
    elif tok.ttype == ID:
        result = VarExp(tok.s)
    elif tok.ttype == LP:
        tok = tokens.next()
        if tok.ttype == ID:
            keywd = tok.s
            if keywd == "while":
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                result = WhileExp(e1, e2)
            elif keywd == "for":
                x = parse_var(tokens)
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                e3 = parse_exp(tokens)
                raise ParseError('Unsupported expression', tok.lineno) # change this!!
            elif keywd == "if":
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                e3 = parse_exp(tokens)
                result = IfExp(e1, e2, e3)
            elif keywd == "write":
                e = parse_exp(tokens)
                result = WriteExp(e)
            elif keywd == "block": # convert to nested seq's on the fly
                es = []
                tok = tokens.next()
                while (tok.ttype != RP):
                    tokens.putback(tok)
                    es.append(parse_exp(tokens))
                    tok = tokens.next()
                tokens.putback(tok)
                if len(es) == 0:
                    es = [IntExp(0)]
                result = es[0]
                for e in es[1:]:
                    result = SeqExp(result,e)
        elif tok.ttype == OPER:
            oper = tok.oper
            if oper == ":=":
                v = parse_var(tokens)
                e = parse_exp(tokens)
                result = AsgnExp(v,e)
            elif oper == "+":
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                result = AddExp(e1, e2)
            elif oper == "-":
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                result = SubExp(e1, e2)
            elif oper == "*":
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                result = MulExp(e1, e2)
            elif oper == "/":
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                result = DivExp(e1, e2)
            elif oper == "<=":
                e1 = parse_exp(tokens)
                e2 = parse_exp(tokens)
                result = LeqExp(e1, e2)
            else:
                raise ParseError("Invalid operator:" + oper, tok.lineno)
        else:
            raise ParseError("Missing or invalid expression", tok.lineno)
        tok = tokens.next()
        if tok.ttype != RP:
            raise ParseError("Missing )", tok.lineno)
    else:
        raise ParseError("Missing or invalid expression", tok.lineno)
    return result

# Parse program
def parse(text):
    tokens = Tokenizer(text)
    exp = parse_exp(tokens)
    tok = tokens.next()
    if tok.ttype != EOF:
        raise ParseError("Extraneous characters at end of program", tok.lineno)
    return exp