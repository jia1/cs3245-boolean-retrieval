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

    def build_from(self, sorted_list):
        if not sorted_list:
            return set_node(None)
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
