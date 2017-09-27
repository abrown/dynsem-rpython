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
class KeywordToken(Token): pass
class OperatorToken(Token): pass
class LeftParensToken(Token): pass
class RightParensToken(Token): pass
class LeftBraceToken(Token): pass
class RightBraceToken(Token): pass
class CommaToken(Token): pass
# TODO path token?


class TokenError(Exception):
    def __init__(self, reason, location):
        self.reason = reason
        self.location = location


def is_whitespace(c):
    return c in ' \t\n\l'
def is_id_char(c):
    return c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/'
def is_keyword(id):
    return id in ["module", "imports", "signature", "constructors", "arrows", "components", "native", "rules"]
def is_operator_char(c):
    return c in '+-*/<>=:|'
def is_number_char(c):
    return c in '0123456789'

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
                    raise TokenError("Unmatched open comment", self.line)
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
            elif is_whitespace(c):
                continue
            # delimiters
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
            # IDs and keywords
            elif is_id_char(c):
                location = self.current_location()
                value = self.read_all_of(c, is_id_char)
                token = KeywordToken(location, value) if is_keyword(value) else IdToken(location, value)
            # operators
            elif is_operator_char(c):
                location = self.current_location()
                value = self.read_all_of(c, is_operator_char)
                token = OperatorToken(location, value)
            # numbers
            elif is_number_char(c):
                location = self.current_location()
                value = self.read_all_of(c, is_number_char)
                token = NumberToken(location, value)
            else:
                raise TokenError('Invalid character: ' + c, self.current_location())

        return token

    def read_all_of(self, value, match_function):
        c = self.read()
        while match_function(c):
            value += c
            c = self.read()
        self.unread()
        return value
