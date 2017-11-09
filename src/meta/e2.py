from src.meta.dynsem import Module, NativeFunction
from src.meta.parser import Parser

e2 = Module()
e2.rules.append(Parser.rule("block([x | xs]) --> block(xs) where x --> y"))
e2.rules.append(Parser.rule("E |- assign(x, v) --> {x |--> v, E}"))
e2.rules.append(Parser.rule("E |- retrieve(x) --> E[x]"))
# TODO not the most elegant but it's what we have to work with
e2.rules.append(Parser.rule("ifz(cond, then, else) --> result where cond --> cond2; case cond2 of {0 => result => else otherwise => result => then}"))
e2.rules.append(Parser.rule("while(cond, then) --> while2(cond, value, then) where cond --> value"))
e2.rules.append(Parser.rule("while2(cond, 0, then) --> 0"))
e2.rules.append(Parser.rule("while2(cond, value, then) --> while(cond, then) where then --> ignored"))


def write(s, unused):
    print(s)
    return 0


e2.native_functions.append(NativeFunction(Parser.term("write(x)"), write))  # TODO rpython demands it
e2.native_functions.append(NativeFunction(Parser.term("add(x, y)"), lambda x, y: x + y))
e2.native_functions.append(NativeFunction(Parser.term("sub(x, y)"), lambda x, y: x - y))
e2.native_functions.append(NativeFunction(Parser.term("mul(x, y)"), lambda x, y: x * y))
e2.native_functions.append(NativeFunction(Parser.term("div(x, y)"), lambda x, y: x // y))
e2.native_functions.append(NativeFunction(Parser.term("leq(x, y)"), lambda x, y: int(x <= y)))
