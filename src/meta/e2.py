from src.meta.dynsem import Module, NativeFunction
from src.meta.parser import Parser

# TODO not the most elegant but it's what we have to work with
while_rule = Parser.rule("while(cond, then) --> while2(cond, value, then) where cond --> value")
while_rule.has_loop = True

rules = [
    Parser.rule("block([x | xs]) --> block(xs) where x --> y"),
    Parser.rule("E |- assign(x, v) --> {x |--> v, E}"),
    Parser.rule("E |- retrieve(x) --> E[x]"),
    # TODO rename this to something other than ifz... it is not an ifz
    Parser.rule(
        "ifz(cond, then, else) --> result where cond --> cond2; case cond2 of {0 => result => else otherwise => result => then}"),
    while_rule,
    Parser.rule("while2(cond, 0, then) --> 0"),
    Parser.rule("while2(cond, value, then) --> while(cond, then) where then --> ignored")
]


def write(s, unused):
    print(s)
    return 0


native_functions = [
    NativeFunction(Parser.native_function("write(x)"), write),  # TODO rpython demands it
    NativeFunction(Parser.native_function("add(x, y)"), lambda x, y: x + y),
    NativeFunction(Parser.native_function("sub(x, y)"), lambda x, y: x - y),
    NativeFunction(Parser.native_function("mul(x, y)"), lambda x, y: x * y),
    NativeFunction(Parser.native_function("div(x, y)"), lambda x, y: x // y),
    NativeFunction(Parser.native_function("leq(x, y)"), lambda x, y: int(x <= y))
]

e2 = Module(rules, native_functions)
