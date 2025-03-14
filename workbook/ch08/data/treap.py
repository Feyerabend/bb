import random

class TreapNode:
    def __init__(self, key, priority=None):
        self.key = key
        self.priority = priority if priority is not None else random.randint(1, 100)
        self.left = None
        self.right = None

class Treap:
    def rotate_right(self, node):
        new_root = node.left
        node.left = new_root.right
        new_root.right = node
        return new_root

    def rotate_left(self, node):
        new_root = node.right
        node.right = new_root.left
        new_root.left = node
        return new_root

    def insert(self, root, key):
        if not root:
            return TreapNode(key)
        if key < root.key:
            root.left = self.insert(root.left, key)
            if root.left.priority > root.priority:
                root = self.rotate_right(root)
        else:
            root.right = self.insert(root.right, key)
            if root.right.priority > root.priority:
                root = self.rotate_left(root)
        return root

    def inorder(self, root):
        if root:
            self.inorder(root.left)
            print(f"{root.key} ({root.priority})", end=" ")
            self.inorder(root.right)

treap = Treap()
root = None
keys = [20, 15, 30, 25, 35, 10, 5]
for key in keys:
    root = treap.insert(root, key)

treap.inorder(root)  # inorder traversal of Treap
