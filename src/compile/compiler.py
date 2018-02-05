import ast
import os

import astor
from src.meta.dynsem import EqualityCheckPremise

class Compiler:
    def compile(self, module):
        template_source = self.get_template_source()
        tree = ast.parse(template_source)
        dispatch_loop = self.find_dispatch_loop(tree)

        id_rule_mapping = self.add_unique_rule_ids(module.rules)
        if_tree = self.construct_if_tree(id_rule_mapping)
        dispatch_loop.body.append(if_tree)

        generated_source = astor.to_source(tree)

        return generated_source

    @staticmethod
    def get_template_source():
        this_directory = os.path.dirname(os.path.realpath(__file__))
        template_file = open(this_directory + '/template.py', 'r')
        template_contents = template_file.read()
        template_file.close()
        return template_contents

    @staticmethod
    def find_dispatch_loop(tree):
        interpreter_class = next(c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == 'Interpreter')
        interpret_method = next(
            m for m in interpreter_class.body if isinstance(m, ast.FunctionDef) and m.name == 'interpret')
        dispatch_loop = next(l for l in interpret_method.body if isinstance(l, ast.While))
        return dispatch_loop

    @staticmethod
    def add_unique_rule_ids(rules):
        id_counter = 0
        name_id_mapping = {}
        id_rule_mapping = {}
        for rule in rules:
            if rule.before.name in name_id_mapping:
                id_rule_mapping[name_id_mapping[rule.before.name]].append(rule)
            else:
                id_counter += 1
                id_rule_mapping[id_counter] = [rule]
                name_id_mapping[rule.before.name] = id_counter
        return id_rule_mapping

    @staticmethod
    def construct_if_tree(id_rule_mapping):
        root_node = None
        current_node = None
        term_var = ast.Name('term', ast.Load)
        term_hash_var = ast.Name('term_hash', ast.Load)
        print_call = ast.Call(ast.Name('print', ast.Load), [term_var], [])
        for id, rules in id_rule_mapping.items():
            for rule in rules:
                comparison_expr = ast.Compare(term_hash_var, [ast.Eq()], [ast.Num(id)])
                if_expr = ast.If(comparison_expr, [ast.Expr(print_call)], [])
                if root_node:
                    current_node.orelse = [if_expr]
                else:
                    root_node = if_expr
                current_node = if_expr
        return root_node

    @staticmethod
    def construct_body(rule):
        tree = None

        for premise in rule.premises:
            if isinstance(premise, EqualityCheckPremise):
                retrieve
        return tree

    @staticmethod
    def retrieve(name, term, tree=None):
        pass
