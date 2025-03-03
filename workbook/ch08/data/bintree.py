class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if not self.root:
            self.root = Node(key)
            return
        queue = [self.root]
        while queue:
            temp = queue.pop(0)
            if not temp.left:
                temp.left = Node(key)
                return
            else:
                queue.append(temp.left)
            if not temp.right:
                temp.right = Node(key)
                return
            else:
                queue.append(temp.right)

    def search(self, root, key):
        if not root:
            return False
        if root.key == key:
            return True
        return self.search(root.left, key) or self.search(root.right, key)

    def inorder(self, root):
        if root:
            self.inorder(root.left)
            print(root.key, end=" ")
            self.inorder(root.right)

    def preorder(self, root):
        if root:
            print(root.key, end=" ")
            self.preorder(root.left)
            self.preorder(root.right)

    def postorder(self, root):
        if root:
            self.postorder(root.left)
            self.postorder(root.right)
            print(root.key, end=" ")

    def level_order(self):
        if not self.root:
            return
        queue = [self.root]
        while queue:
            temp = queue.pop(0)
            print(temp.key, end=" ")
            if temp.left:
                queue.append(temp.left)
            if temp.right:
                queue.append(temp.right)

    def height(self, root):
        if not root:
            return 0
        return 1 + max(self.height(root.left), self.height(root.right))

    def delete(self, key):
        if not self.root:
            return None
        if self.root.key == key and not self.root.left and not self.root.right:
            self.root = None
            return

        queue = [self.root]
        target, last = None, None

        while queue:
            last = queue.pop(0)
            if last.key == key:
                target = last
            if last.left:
                queue.append(last.left)
            if last.right:
                queue.append(last.right)

        if target:
            target.key = last.key
            queue = [self.root]
            while queue:
                temp = queue.pop(0)
                if temp.left == last:
                    temp.left = None
                    return
                elif temp.left:
                    queue.append(temp.left)
                if temp.right == last:
                    temp.right = None
                    return
                elif temp.right:
                    queue.append(temp.right)

# example
tree = BinaryTree()
for key in [10, 20, 30, 40, 50, 60, 70]:
    tree.insert(key)

print("Inorder Traversal:")
tree.inorder(tree.root)
print("\nPreorder Traversal:")
tree.preorder(tree.root)
print("\nPostorder Traversal:")
tree.postorder(tree.root)
print("\nLevel-order Traversal:")
tree.level_order()
print("\nHeight of Tree:", tree.height(tree.root))

tree.delete(30)
print("\nInorder Traversal after deleting 30:")
tree.inorder(tree.root)