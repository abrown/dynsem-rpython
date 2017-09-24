class Node:
    def eval(self, context):
        pass  # should return transformed holes, next node, and the modified environment

    def transform(self, holes):
        return holes


class Context:
    def __init__(self, previous_node, next_node, holes = [], environment = None):
        self.previous = previous_node
        self.next = next_node
        self.holes = holes
        self.environment = environment


class ConstructorNode(Node):
    def __init__(self, term, hole_filter, hole_additions, next_node):
        self.term = term
        self.hole_map = hole_filter
        self.hole_additions = hole_additions
        self.next_node = next_node

    def eval(self, context):
        holes = [context.holes[i] for i in self.hole_map]
        for i in self.hole_additions:
            holes.insert(i, self.hole_additions[i])

        context.holes = holes
        context.previous = self
        context.next = self.next_node
        return context


class TypeCheckNode(Node):
    def __init__(self, term_type, left_node, right_node):
        self.term_type = term_type
        self.left_node = left_node
        self.right_node = right_node

    def eval(self, context):
        context.next = self.left_node if self.left_node.term_type == self.term_type else self.right_node
        context.previous = self
        return context


class StartNode(Node):
    def __init__(self):
        self.term = None

    def from_term(self, term):
        self.term = term
        return self

    def eval(self, context=None):
        pass


class EndNode(Node):
    def term_of(self, holes):
        pass


class Interpreter:
    def eval(self, start_node, term):
        assert isinstance(start_node, StartNode)
        context = start_node.from_term(term).eval()

        while not isinstance(context.next, EndNode):
            context = context.next.eval(context)

        assert isinstance(context.next, EndNode)
        return context.next.term_of(context.holes)
