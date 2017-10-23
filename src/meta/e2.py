from src.meta.dynsem import Module, NativeFunction
from src.meta.parser import Parser

e2 = Module()
e2.rules.append(Parser.rule("block([x | xs]) --> block(xs) where x --> y"))
e2.rules.append(Parser.rule("E |- assign(x, v) --> {x |--> v, E}"))
e2.rules.append(Parser.rule("E |- retrieve(x) --> E[x]"))
e2.rules.append(
    Parser.rule("ifz(cond, then, else) --> result where cond --> cond2; case cond2 of {0 => result => else otherwise => result => then}"))
e2.rules.append(
    Parser.rule("while(cond, then) --> result where case cond of {0 => result => cond otherwise => then --> result}"))


def write(s):
    print(s)
    return None


e2.native_functions.append(NativeFunction(Parser.term("write(x)"), write))
e2.native_functions.append(NativeFunction(Parser.term("add(x, y)"), lambda x, y: x + y))
e2.native_functions.append(NativeFunction(Parser.term("sub(x, y)"), lambda x, y: x - y))
e2.native_functions.append(NativeFunction(Parser.term("mul(x, y)"), lambda x, y: x * y))
e2.native_functions.append(NativeFunction(Parser.term("div(x, y)"), lambda x, y: x / y))
e2.native_functions.append(NativeFunction(Parser.term("leq(x, y)"), lambda x, y: int(x <= y)))
