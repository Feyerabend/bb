class Node:
    def __init__(self, point):
        self.point = point  # point in k-dimensional space
        self.left = None
        self.right = None


class KDTree:
    def __init__(self, k):
        self.k = k  # num of dimensions
        self.root = None

    def insert(self, root, point, depth=0):
        # base case: if tree empty, create new node
        if root is None:
            return Node(point)

        # calc current dimension (based on depth)
        cd = depth % self.k

        # recursively insert the point
        if point[cd] < root.point[cd]:
            root.left = self.insert(root.left, point, depth + 1)
        else:
            root.right = self.insert(root.right, point, depth + 1)

        return root

    def build(self, points):
        for point in points:
            self.root = self.insert(self.root, point)

    def inorder_traversal(self, root):
        if root:
            self.inorder_traversal(root.left)
            print(root.point)
            self.inorder_traversal(root.right)

    def print_tree(self):
        print("K-D Tree Inorder Traversal:")
        self.inorder_traversal(self.root)


# example
points = [
    [3, 6],
    [17, 15],
    [13, 15],
    [6, 12],
    [9, 1],
    [2, 7],
    [10, 19]
]

kdtree = KDTree(k=2)  # 2D K-D tree
kdtree.build(points)
kdtree.print_tree()
