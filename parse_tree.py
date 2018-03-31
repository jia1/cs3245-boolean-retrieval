from collections import deque
from skip_list import SkipList
from constants import operators, identity, peek

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

    def is_leaf(self): return not self.has_left() and not self.has_right()
    def is_operand(self): return self.is_leaf()
    def is_operator(self): return not self.is_operand()

    def get_data(self): return self.data
    def get_left(self): return self.left
    def get_right(self): return self.right
    def get_parent(self): return self.parent

    def set_data(self, data): self.data = data
    def set_left(self, left): self.left = left
    def set_right(self, right): self.right = right
    def set_parent(self, parent): self.parent = parent

    def print_node(self):
        print('ParseTreeNode')
        print('^:\t{}'.format(self.parent.data if self.parent is not None else None))
        print('.:\t{}'.format(self.data))
        print('<:\t{}'.format(self.left.data if self.left is not None else None))
        print('>:\t{}'.format(self.right.data if self.right is not None else None))
        print()

class ParseTree:
    root = None
    leaves = set()

    def __init__(self, root=None, leaves=None):
        self.root = root
        if leaves is not None:
            self.leaves = leaves

    def get_root(self): return self.root
    def set_root(self, root): self.root = root

    def reload_leaves(self):
        self.leaves = set()
        queue = deque((self.root,))
        while queue:
            node = queue.popleft()
            if node.is_leaf():
                self.leaves.add(node)
                continue
            if node.has_left():
                queue.append(node.get_left())
            if node.has_right():
                queue.append(node.get_right())

    def get_sorted_leaves(self, comparator=identity):
        self.reload_leaves()
        return sorted(self.leaves, key=comparator)

    def get_sorted_operands(self, comparator=identity):
        return self.get_sorted_leaves(comparator)

    def build_from(self, postfix_list):
        stack = []
        nodes = map(lambda data: ParseTreeNode(data=data), postfix_list)
        for node in nodes:
            token = node.get_data()
            if token not in operators:
                stack.append(node)
            else:
                left_node = peek(stack, error='Insufficient number of operands')
                left_node.set_parent(node)
                node.set_left(left_node)
                stack.pop()
                # Always binary operator
                right_node = peek(stack, error='Insufficient number of operands')
                right_node.set_parent(node)
                node.set_right(right_node)
                stack.pop()
                # End of if binary operator block
                stack.append(node)
        if stack:
            self.root = stack.pop()
