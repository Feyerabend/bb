class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # Minimum degree (defines range for number of keys)
        self.leaf = leaf  # True if leaf node
        self.keys = []  # List of keys
        self.children = []  # List of children

    def __str__(self):
        return str(self.keys)

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, True)
        self.t = t

    def search(self, key, node=None):
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and node.keys[i] == key:
            return node

        if node.leaf:
            return None

        return self.search(key, node.children[i])

    def insert(self, key):
        root = self.root

        if len(root.keys) == (2 * self.t) - 1:
            new_root = BTreeNode(self.t, False)
            new_root.children.append(root)
            self.split_child(new_root, 0)
            self.root = new_root

        self.insert_non_full(self.root, key)

    def insert_non_full(self, node, key):
        i = len(node.keys) - 1

        if node.leaf:
            node.keys.append(0)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            if len(node.children[i].keys) == (2 * self.t) - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1

            self.insert_non_full(node.children[i], key)

    def split_child(self, parent, i):
        t = self.t
        node = parent.children[i]
        new_node = BTreeNode(t, node.leaf)
        
        parent.keys.insert(i, node.keys[t - 1])
        parent.children.insert(i + 1, new_node)

        new_node.keys = node.keys[t:(2 * t) - 1]
        node.keys = node.keys[0:t - 1]

        if not node.leaf:
            new_node.children = node.children[t:(2 * t)]
            node.children = node.children[0:t]

    def traverse(self, node=None):
        if node is None:
            node = self.root
        for i in range(len(node.keys)):
            if not node.leaf:
                self.traverse(node.children[i])
            print(node.keys[i], end=" ")
        if not node.leaf:
            self.traverse(node.children[len(node.keys)])

# example
btree = BTree(2)
for key in [10, 20, 5, 6, 12, 30, 7, 17]:
    btree.insert(key)

print("B-Tree traversal:")
btree.traverse()
print()

print("Search for 12:", "Found" if btree.search(12) else "Not Found")
print("Search for 99:", "Found" if btree.search(99) else "Not Found")
