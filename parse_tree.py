from collections import deque
from skip_list import SkipList

identity = lambda x: x
operators = ['or', 'and', 'not']

# Accepts an operator string (e.g. 'not', 'or', 'and') and
# Returns True only if the operator is a binary operator (i.e. 'or', 'and')
def is_binary_operator(operator):
    return operator.lower() != 'not'

# Accepts a stack (list type)
# And returns the last element (also last-in)
def peek(stack, error='Peek from empty stack'):
    if not stack:
        sys.exit(error)
    return stack[-1]

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
    def is_unary_operator(self): return self.has_left() and not self.has_right()
    def is_binary_operator(self): return self.has_left() and self.has_right()

    def get_data(self): return self.data
    def get_left(self): return self.left
    def get_right(self): return self.right
    def get_parent(self): return self.parent

    def set_data(self, data): self.data = data
    def set_left(self, left): self.left = left
    def set_right(self, right): self.right = right
    def set_parent(self, parent): self.parent = parent

    def print_node(self):
        print('NODE')
        print('parent:\t{}'.format(self.parent if self.parent is None else self.parent.data))
        print('self:\t{}'.format(self.data))
        print('left:\t{}'.format(self.left if self.left is None else self.left.data))
        print('right:\t{}'.format(self.right if self.right is None else self.right.data))
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
                if is_binary_operator(token):
                    right_node = peek(stack, error='Insufficient number of operands')
                    right_node.set_parent(node)
                    node.set_right(right_node)
                    stack.pop()
                stack.append(node)
        if stack:
            self.root = stack.pop()