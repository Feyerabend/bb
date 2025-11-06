class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class SplayTree:
    def __init__(self):
        self.root = None

    def _right_rotate(self, node):
        left_child = node.left
        node.left = left_child.right
        left_child.right = node
        return left_child

    def _left_rotate(self, node):
        right_child = node.right
        node.right = right_child.left
        right_child.left = node
        return right_child

    def _splay(self, root, key):
        if root is None or root.key == key:
            return root
        
        if key < root.key:
            if root.left is None:
                return root
            if key < root.left.key:
                root.left.left = self._splay(root.left.left, key)
                root = self._right_rotate(root)
            elif key > root.left.key:
                root.left.right = self._splay(root.left.right, key)
                if root.left.right:
                    root.left = self._left_rotate(root.left)
            return self._right_rotate(root) if root.left else root
        else:
            if root.right is None:
                return root
            if key > root.right.key:
                root.right.right = self._splay(root.right.right, key)
                root = self._left_rotate(root)
            elif key < root.right.key:
                root.right.left = self._splay(root.right.left, key)
                if root.right.left:
                    root.right = self._right_rotate(root.right)
            return self._left_rotate(root) if root.right else root

    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
            return
        self.root = self._splay(self.root, key)
        if key == self.root.key:
            return
        new_node = Node(key)
        if key < self.root.key:
            new_node.right = self.root
            new_node.left = self.root.left
            self.root.left = None
        else:
            new_node.left = self.root
            new_node.right = self.root.right
            self.root.right = None
        self.root = new_node

    def search(self, key):
        self.root = self._splay(self.root, key)
        return self.root and self.root.key == key

    def inorder_traversal(self, node):
        if node:
            self.inorder_traversal(node.left)
            print(node.key, end=" ")
            self.inorder_traversal(node.right)


tree = SplayTree()
for val in [10, 20, 30, 40, 50]:
    tree.insert(val)

tree.inorder_traversal(tree.root)
print("\nSearching for 30:", tree.search(30))
print("Searching for 100:", tree.search(100))