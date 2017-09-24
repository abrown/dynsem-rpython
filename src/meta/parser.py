class Location:
    def __init__(self, offset, line, file):
        self.offset = offset
        self.line = line
        self.file = file

    def __repr__(self):
        return "{}:{}".format(self.file if self.file else "<code string>", self.line)


class Token:
    def __init__(self, location=None, value=None):
        self.location = location
        self.value = value

    def __repr__(self):
        return "{}{} at {}".format(self.__class__.__name__, "=" + self.value if self.value else "", self.location)


class EofToken(Token): pass
class NumberToken(Token): pass
class IdToken(Token): pass
class OperatorToken(Token): pass
class LeftParensToken(Token): pass
class RightParensToken(Token): pass
class LeftBraceToken(Token): pass
class RightBraceToken(Token): pass
class CommaToken(Token): pass


class ParseError(Exception):
    def __init__(self, reason, location):
        self.reason = reason
        self.location = location


class Tokenizer:
    def __init__(self, text, file=None):
        self.text = text
        self.global_offset = 0
        self.line_offset = 0
        self.line = 1
        self.file = file
        self.in_line_comment = False
        self.in_multiline_comment = False

    def read(self):
        if self.global_offset < len(self.text):
            char = self.text[self.global_offset]
            self.global_offset += 1
            self.line_offset += 1
            return char
        else:
            return ''

    def peek(self):
        if self.global_offset < len(self.text):
            return self.text[self.global_offset]
        else:
            return ''

    def unread(self):
        self.global_offset -= 1

    def current_location(self):
        return Location(self.line_offset, self.line, self.file)

    def next(self):
        token = None
        while not token:
            c = self.read()
            if c == '':
                if self.in_line_comment or self.in_multiline_comment:
                    raise ParseError("Unmatched open comment", self.line)
                else:
                    token = EofToken(self.current_location())
            # new lines
            elif c == '\n':
                self.line += 1
                self.line_offset = 0
                self.in_line_comment = False
                continue
            # comments
            elif self.in_line_comment:
                continue
            elif self.in_multiline_comment:
                if c == '*' and self.peek() == '/':
                    self.read()  # eliminate the /
                    self.in_multiline_comment = False
            elif c == '/' and self.peek() == '/':
                self.read()  # eliminate the /
                self.in_line_comment = True
            elif c == '/' and self.peek() == '*':
                self.in_multiline_comment = True
            # white space
            elif self.is_whitespace(c):
                continue
            elif c == '(':
                token = LeftParensToken(self.current_location())
            elif c == ')':
                token = RightParensToken(self.current_location())
            elif c == '{':
                token = LeftBraceToken(self.current_location())
            elif c == '}':
                token = RightBraceToken(self.current_location())
            elif c == ',':
                token = CommaToken(self.current_location())
            elif self.is_id_char(c):
                location = self.current_location()
                value = self.read_all_of(c, self.is_id_char)
                token = IdToken(location, value)
            elif self.is_operator_char(c):
                location = self.current_location()
                value = self.read_all_of(c, self.is_operator_char)
                token = OperatorToken(location, value)
            else:
                raise ParseError('Invalid character: ' + c, self.current_location())

        return token

    def read_all_of(self, value, match_function):
        c = self.read()
        while match_function(c):
            value += c
            c = self.read()
        self.unread()
        return value

    def is_whitespace(self, c):
        return c in ' \t\n\l'

    def is_id_char(self, c):
        return c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/'

    def is_operator_char(self, c):
        return c in '+-*/<>=:|'
        # elif c == '{':
        #                 comment_level += 1
        #                 continue
        #             elif c == '}':
        #                 if comment_level > 0:
        #                     comment_level -= 1
        #                     continue
        #                 else:
        #                     raise ParseError("Unmatched close comment", self.lineno)
        #             elif comment_level > 0:
        #                 continue
        #             elif is_whitespace(c):
        #                 continue
        #             elif c == '(':
        #                 result = mkLP(self.lineno)
        #             elif c == ')':
        #                 result = mkRP(self.lineno)
        #             elif is_num_char(c):
        #                 s = c
        #                 c = self.readc()
        #                 while (is_num_char(c)):
        #                     s = s + c
        #                     c = self.readc()
        #                 self.unreadc()
        #                 result = mkNUM(int(s), self.lineno)
        #             elif is_oper_char(c):
        #                 s = c
        #                 c = self.readc()
        #                 while is_oper_char(c):
        #                     s = s + c
        #                     c = self.readc()
        #                 self.unreadc()
        #                 result = mkOPER(s, self.lineno)
        #             elif is_id_char(c):
        #                 s = c
        #                 c = self.readc()
        #                 while is_id_char(c):
        #                     s = s + c
        #                     c = self.readc()
        #                 self.unreadc()
        #                 result = mkID(s, self.lineno)
        #             else:
        #                 raise ParseError('Invalid character:' + c, self.lineno)
        #         return result
        #
        #

#
# # Token type (ttype) codes

#
# class Token:
#     def __init__(self, ttype, lineno):
#         self.ttype = ttype
#         self.lineno = lineno
#
# def mkNUM(num, lineno):
#     t = Token(NUM, lineno)
#     t.num = num
#     return t
#
# def mkOPER(oper, lineno):
#     t = Token(OPER, lineno)
#     t.oper = oper
#     return t
#
# def mkID(s, lineno):
#     t = Token(ID, lineno)
#     t.s = s
#     return t
#
# def mkLP(lineno):
#     return Token(LP, lineno)
#
# def mkRP(lineno):
#     return Token(RP, lineno)
#
# def mkEOF(lineno):
#     return Token(EOF, lineno)
#
#
#
#
# def is_num_char(c):
#     return c in '0123456789'
#
# def is_oper_char(c):
#     return c in '+-*/<=:='
#
# def is_id_char(c):
#     return c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
#
# # Lexical analysis
#
#
# # Token generator
# class Tokenizer:
#     def __init__(self, text):
#         self.text = text
#         self.char = 0
#         self.lineno = 1
#         self.cache = None
#
#     def readc(self):
#         if (self.char < len(self.text)):
#             c = self.text[self.char]
#             self.char += 1
#             return c
#         else:
#             return ''
#
#     def unreadc(self):
#         self.char -= 1
#
#     def next(self):
#         result = self.cache
#         self.cache = None
#         comment_level = 0
#         while (not result):
#             c = self.readc()
#             if c == '':
#                 if comment_level > 0:
#                     raise ParseError("Unmatched open comment", self.lineno)
#                 else:
#                     result = mkEOF(self.lineno)
#             elif c == '\n':
#                 self.lineno += 1
#                 continue
#             elif c == '{':
#                 comment_level += 1
#                 continue
#             elif c == '}':
#                 if comment_level > 0:
#                     comment_level -= 1
#                     continue
#                 else:
#                     raise ParseError("Unmatched close comment", self.lineno)
#             elif comment_level > 0:
#                 continue
#             elif is_whitespace(c):
#                 continue
#             elif c == '(':
#                 result = mkLP(self.lineno)
#             elif c == ')':
#                 result = mkRP(self.lineno)
#             elif is_num_char(c):
#                 s = c
#                 c = self.readc()
#                 while (is_num_char(c)):
#                     s = s + c
#                     c = self.readc()
#                 self.unreadc()
#                 result = mkNUM(int(s), self.lineno)
#             elif is_oper_char(c):
#                 s = c
#                 c = self.readc()
#                 while is_oper_char(c):
#                     s = s + c
#                     c = self.readc()
#                 self.unreadc()
#                 result = mkOPER(s, self.lineno)
#             elif is_id_char(c):
#                 s = c
#                 c = self.readc()
#                 while is_id_char(c):
#                     s = s + c
#                     c = self.readc()
#                 self.unreadc()
#                 result = mkID(s, self.lineno)
#             else:
#                 raise ParseError('Invalid character:' + c, self.lineno)
#         return result
#
#     def putback(self, tok):
#         self.cache = tok
#
#
# def tokenize(program):
#     for number, operator in token_pat.findall(program):
#         if number:
#             yield literal_token(number)
#         elif operator == "+":
#             yield operator_add_token()
#         else:
#             raise SyntaxError("unknown operator")
#     yield end_token()
#
# def next():
#
#
# def expression(t1=None, rbp=0):
#     if not t1:
#         t1 = next()
#     t2 = next()
#     left = t1.nud()
#     while rbp < t2.lbp:
#         t1 = t2
#         t2 = next()
#         left = t1.led(left)
#     return left
