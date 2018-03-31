### WARNING: THIS SKIP LIST IMPLEMENTATION DOES NOT HAVE METHODS TO VERIFY OPERATOR ARITY ###

from math import sqrt

class SkipListNode:
    data = None
    next_node = None
    skip_node = None

    def __init__(self, data=None, next_node=None, skip_node=None):
        self.data = data
        self.next_node = next_node
        self.skip_node = skip_node

    def get_data(self): return self.data
    def get_next(self): return self.next_node
    def get_skip(self): return self.skip_node

    def set_next(self, next_node): self.next_node = next_node
    def set_skip(self, skip_node): self.skip_node = skip_node

class SkipList:
    head = None
    last = None
    length = 0

    def __init__(self, node=None):
        if node is not None:
            self.head = node

    def get_head(self): return self.head
    def get_last(self): return self.last

    def get_length(self):
        if self.head is not None and self.length == 0:
            node = self.head
            length = 1
            while node.get_next() is not None:
                length += 1
            self.last = node
            self.length = length
        return self.length

    def reset(self):
        self.head = None
        self.last = None
        self.length = 0

    def build_from(self, sorted_list):
        if not sorted_list:
            return self.reset()
        self.length = len(sorted_list)
        step = round(sqrt(self.length - 1))
        nodes = list(map(
            lambda data: SkipListNode(data),
            sorted_list))
        for i in range(self.length - 1):
            nodes[i].set_next(nodes[i + 1])
        if step:
            for i in range(0, self.length - step, step):
                nodes[i].set_skip(nodes[i + step])
        self.head = nodes[0]
        self.last = nodes[-1]

    def to_list(self):
        node = self.head
        data = []
        while node is not None:
            data.append(node.get_data())
            node = node.get_next()
        return data

    # Implementation of (skip list A).AND(skip list B) (Moved over from search.py)
    # Accepts one skip list and returns a new skip list containing postings which both skip lists have
    # Does skipping when the skip pointer node of one skip list has a value less than the other skip list node
    def merge(skip_list_b):
        merged_skip_list_data = []
        node_a = self.get_head()
        node_b = skip_list_b.get_head()
        while node_a is not None and node_b is not None:
            data_a = node_a.get_data()
            data_b = node_b.get_data()
            if data_a < data_b:
                skip_node_a = node_a.get_skip()
                if skip_node_a is not None and skip_node_a.get_data() <= data_b:
                    node_a = skip_node_a
                else:
                    node_a = node_a.get_next()
            elif data_b < data_a:
                skip_node_b = node_b.get_skip()
                if skip_node_b is not None and skip_node_b.get_data() <= data_a:
                    node_b = skip_node_b
                else:
                    node_b = node_b.get_next()
            else: # data_a == data_b:
                merged_skip_list_data.append(data_a)
                node_a = node_a.get_next()
                node_b = node_b.get_next()
        merged_skip_list = SkipList()
        merged_skip_list.build_from(merged_skip_list_data)
        return merged_skip_list
