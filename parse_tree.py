from collections import deque
from skip_list import SkipList
from search import operators, is_binary_operator, peek

identity = lambda x: x

class ParseTreeNode:
    data = None
    left = None
    right = None
    parent = None

    def __init__(self, data=None, left=None, right=None, parent=None):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

    def has_left(self): return self.left is not None
    def has_right(self): return self.right is not None
    def has_parent(self): return self.parent is not None

    def is_root(self): return not self.has_parent()
    def is_evaluated(self): return self.is_root()

    def is_leaf(self): return self.has_left() and self.has_right()
    def is_operand(self): return self.is_leaf()
    def is_operator(self): return not self.is_operand()
    def is_unary_operator(self): return self.is_operator() and not self.has_right()

    def get_data(self): return self.data
    def get_left(self): return self.left
    def get_right(self): return self.right
    def get_parent(self): return self.parent

    def set_data(self, data): self.data = data
    def set_left(self, left): self.left = left
    def set_right(self, right): self.right = right
    def set_parent(self, parent): self.parent = parent

class ParseTree:
    root = None
    leaves = set()

    def __init__(self, root=None, leaves=None):
        self.root = root
        if leaves is not None:
            self.leaves = leaves

    def get_root(self): return self.root
    def set_root(self, root): self.root = root

    def add_leaf(self, leaf): leaves.add(leaf)

    def reload_leaves(self):
        queue = dequeue((self.root,))
        while queue:
            node = queue.popleft()
            if node.is_leaf():
                self.leaves.add(node)
                continue
            if node.has_left():
                queue.append(node.get_left())
            if node.has_right():
                queue.append(node.get_right())

    def get_minimum_leaf(self, comparator=identity):
        '''
        if leaves:
            return min(leaves, key=comparator)
        '''
        self.reload_leaves()
        return self.get_minimum_leaf(comparator)

    def get_minimum_operand(self, comparator=identity):
        return get_minimum_leaf(comparator)

    def build_from(self, postfix_list):
        stack = []
        for token in postfix_list:
            if token not in operators:
                stack.append(token)
            else:
                operator_node = ParseTreeNode(data=token)
                left_operand = peek(stack, error='Insufficient number of operands')
                operator_node.set_left(ParseTreeNode(data=left_operand, parent=operator_node))
                stack.pop()
                if is_binary_operator(token):
                    right_operand = peek(stack, error='Insufficient number of operands')
                    operator_node.set_right(ParseTreeNode(data=right_operand, parent=operator_node))
                    stack.pop()
                stack.append(operator_node)
        if stack:
            self.root = stack.pop()
