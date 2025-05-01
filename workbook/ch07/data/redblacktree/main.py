class Node:
    def __init__(self, key, value=None, color=1):
        self.key = key
        self.value = value
        self.parent = None
        self.left = None
        self.right = None
        self.color = color  # 1 for RED, 0 for BLACK

class RedBlackTree:
    def __init__(self):
        self.NIL = Node(None, None, 0)  # sentinel node (nil), colored BLACK
        self.root = self.NIL

    def search(self, key):
        return self._search_helper(self.root, key)

    def _search_helper(self, node, key):
        if node == self.NIL:
            return None
        
        if key == node.key:
            return node.value
        elif key < node.key:
            return self._search_helper(node.left, key)
        else:
            return self._search_helper(node.right, key)

    def insert(self, key, value=None):
        # Create new node
        new_node = Node(key, value, 1)  # RED node
        new_node.left = self.NIL
        new_node.right = self.NIL
        
        # Find position to insert
        y = None
        x = self.root
        
        while x != self.NIL:
            y = x
            if new_node.key < x.key:
                x = x.left
            elif new_node.key > x.key:
                x = x.right
            else:
                # Key already exists, update value
                x.value = value
                return
        
        # Set parent of new node
        new_node.parent = y
        
        # Insert new node
        if y is None:
            self.root = new_node
        elif new_node.key < y.key:
            y.left = new_node
        else:
            y.right = new_node
            
        # Fix Red-Black Tree properties
        self._fix_insert(new_node)

    def _fix_insert(self, k):
        while k != self.root and k.parent.color == 1:  # RED
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left  # uncle
                if u.color == 1:  # RED
                    u.color = 0  # BLACK
                    k.parent.color = 0  # BLACK
                    k.parent.parent.color = 1  # RED
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self._right_rotate(k)
                    k.parent.color = 0  # BLACK
                    k.parent.parent.color = 1  # RED
                    self._left_rotate(k.parent.parent)
            else:
                u = k.parent.parent.right  # uncle
                if u.color == 1:  # RED
                    u.color = 0  # BLACK
                    k.parent.color = 0  # BLACK
                    k.parent.parent.color = 1  # RED
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self._left_rotate(k)
                    k.parent.color = 0  # BLACK
                    k.parent.parent.color = 1  # RED
                    self._right_rotate(k.parent.parent)
            
            if k == self.root:
                break
                
        self.root.color = 0  # BLACK

    def delete(self, key):
        self._delete_node(self.root, key)

    def _delete_node(self, node, key):
        z = self.NIL
        while node != self.NIL:
            if node.key == key:
                z = node
                break
            elif node.key > key:
                node = node.left
            else:
                node = node.right
                
        if z == self.NIL:
            return False  # Key not found
            
        y = z
        y_original_color = y.color
        
        if z.left == self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
                
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
            
        if y_original_color == 0:  # BLACK
            self._fix_delete(x)
            
        return True

    def _fix_delete(self, x):
        while x != self.root and x.color == 0:  # BLACK
            if x == x.parent.left:
                s = x.parent.right
                if s.color == 1:  # RED
                    s.color = 0  # BLACK
                    x.parent.color = 1  # RED
                    self._left_rotate(x.parent)
                    s = x.parent.right
                    
                if s.left.color == 0 and s.right.color == 0:  # Both BLACK
                    s.color = 1  # RED
                    x = x.parent
                else:
                    if s.right.color == 0:  # BLACK
                        s.left.color = 0  # BLACK
                        s.color = 1  # RED
                        self._right_rotate(s)
                        s = x.parent.right
                        
                    s.color = x.parent.color
                    x.parent.color = 0  # BLACK
                    s.right.color = 0  # BLACK
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                s = x.parent.left
                if s.color == 1:  # RED
                    s.color = 0  # BLACK
                    x.parent.color = 1  # RED
                    self._right_rotate(x.parent)
                    s = x.parent.left
                    
                if s.right.color == 0 and s.left.color == 0:  # Both BLACK
                    s.color = 1  # RED
                    x = x.parent
                else:
                    if s.left.color == 0:  # BLACK
                        s.right.color = 0  # BLACK
                        s.color = 1  # RED
                        self._left_rotate(s)
                        s = x.parent.left
                        
                    s.color = x.parent.color
                    x.parent.color = 0  # BLACK
                    s.left.color = 0  # BLACK
                    self._right_rotate(x.parent)
                    x = self.root
                    
        x.color = 0  # BLACK

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _minimum(self, node):
        while node.left != self.NIL:
            node = node.left
        return node

    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        
        if y.left != self.NIL:
            y.left.parent = x
            
        y.parent = x.parent
        
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
            
        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        
        if y.right != self.NIL:
            y.right.parent = x
            
        y.parent = x.parent
        
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
            
        y.right = x
        x.parent = y

    def inorder(self):
        result = []
        self._inorder_helper(self.root, result)
        return result

    def _inorder_helper(self, node, result):
        if node != self.NIL:
            self._inorder_helper(node.left, result)
            result.append((node.key, node.value, "RED" if node.color == 1 else "BLACK"))
            self._inorder_helper(node.right, result)

    def is_empty(self):
        return self.root == self.NIL

def test_red_black_tree():
    # Test Case 0: Insert nodes
    print("Test Case 0: Insert nodes")
    tree = RedBlackTree()
    tree.insert("Athena", "Wisdom")
    tree.insert("Zeus", "Thunder")
    tree.insert("Hades", "Underworld")
    tree.insert("Poseidon", "Sea")
    tree.insert("Hermes", "Messenger")
    tree.insert("Demeter", "Harvest")
    tree.insert("Dionysus", "Wine")
    tree.insert("Ares", "War")
    tree.insert("Artemis", "Hunt")
    tree.insert("Hephaestus", "Forge")
    print("Inorder Walk:")
    print(tree.inorder())
    print()

    # Create a new tree for the rest of the test cases
    tree = RedBlackTree()

    # Test Case 1: Empty Tree
    print("Test Case 1: Empty Tree")
    print(f"Search for 'Athena': {'Not Found' if tree.search('Athena') is None else 'Found'}")
    tree.delete("Athena")  # Should do nothing
    print()

    # Test Case 2: Single Node Tree
    print("Test Case 2: Single Node Tree")
    tree.insert("Athena", "Wisdom")
    print("Inorder Walk:")
    print(tree.inorder())
    print(f"Search for 'Athena': {'Not Found' if tree.search('Athena') is None else 'Found'}")
    tree.delete("Athena")  # Delete the root
    print("Inorder Walk after deletion:")
    print(tree.inorder())
    print()

    # Test Case 3: Insertion of Duplicate Keys
    print("Test Case 3: Insertion of Duplicate Keys")
    tree.insert("Athena", "Wisdom")
    tree.insert("Athena", "New Value")  # Update value
    print("Inorder Walk:")
    print(tree.inorder())
    print()

    # Test Case 4: Deletion of Non-Existent Keys
    print("Test Case 4: Deletion of Non-Existent Keys")
    tree.delete("NonExistentKey")  # Should do nothing
    print("Inorder Walk:")
    print(tree.inorder())
    print()

    # Test Case 5: Deletion of Root Node
    print("Test Case 5: Deletion of Root Node")
    tree.insert("Zeus", "Thunder")
    tree.insert("Hades", "Underworld")
    print("Inorder Walk before deletion:")
    print(tree.inorder())
    print()
    tree.delete("Hades")
    print("Inorder Walk after deletion:")
    print(tree.inorder())
    print()

    # Test Case 6: Deletion of Leaf Nodes
    print("Test Case 6: Deletion of Leaf Nodes")
    tree.insert("Poseidon", "Sea")
    print("Inorder Walk before deletion:")
    print(tree.inorder())
    print()
    tree.delete("Athena")  # Delete leaf node
    print("Inorder Walk after deletion:")
    print(tree.inorder())
    print()

    # Test Case 7: Deletion of Nodes with One Child
    print("Test Case 7: Deletion of Nodes with One Child")
    tree.insert("Hermes", "Messenger")
    tree.insert("Demeter", "Harvest")
    print("Inorder Walk before deletion:")
    print(tree.inorder())
    print()
    tree.delete("Hermes")  # Delete node with one child
    print("Inorder Walk after deletion:")
    print(tree.inorder())
    print()

    # Test Case 8: Deletion of Nodes with Two Children
    print("Test Case 8: Deletion of Nodes with Two Children")
    tree.insert("Dionysus", "Wine")
    tree.insert("Ares", "War")
    print("Inorder Walk before deletion:")
    print(tree.inorder())
    print()
    tree.delete("Demeter")  # Delete node with two children
    print("Inorder Walk after deletion:")
    print(tree.inorder())
    print()

    # Test Case 9: Large Tree Stress Test
    print("Test Case 9: Large Tree Stress Test")
    for i in range(100):
        key = f"Key{i}"
        value = f"Value{i}"
        tree.insert(key, value)
    
    print("Inorder Walk after insertions (showing only first 10 items):")
    full_inorder = tree.inorder()
    print(full_inorder[:10])
    print("...")
    
    for i in range(100):
        key = f"Key{i}"
        tree.delete(key)
    
    print("Inorder Walk after deletions:")
    print(tree.inorder())
    print()

if __name__ == "__main__":
    test_red_black_tree()
