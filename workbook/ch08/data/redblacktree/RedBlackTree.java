
/*  Red-Black Tree
 *  Set Lonnert, 1999
 *   See:
 *     Introduction to Algorithms,
 *     eds. Thomas H. Cormen, Charles E. Leiserson & Ronald L. Rivest
 *     (1990), 7th print (Cambridge, Mass: MIT Press, 1996).
 */

import java.util.*;

abstract class Node { }

class RedBlackTreeNode extends Node {
    Object key, value;
    int color; // 0 for RED, 1 for BLACK
    RedBlackTreeNode left, right, parent;

    // Constructor
    RedBlackTreeNode(Object key, Object value) {
        this.key = key;
        this.value = value;
        this.color = 0; // RED by default
        this.left = this.right = this.parent = null;
    }
}

class RedBlackTree {
    private RedBlackTreeNode root;
    public final RedBlackTreeNode nil;
    private static final int RED = 0;
    private static final int BLACK = 1;

    // Constructor
    public RedBlackTree() {
        nil = new RedBlackTreeNode(null, null);
        nil.color = BLACK; // always BLACK
        root = nil;
    }

    public boolean isEmpty() {
        return root == nil;
    }

    private RedBlackTreeNode getRoot() {
        return root;
    }

    private int color(RedBlackTreeNode node) {
        return node == nil ? BLACK : node.color;
    }

    private RedBlackTreeNode minimum(RedBlackTreeNode node) {
        while (node.left != nil) {
            node = node.left;
        }
        return node;
    }

    private RedBlackTreeNode successor(RedBlackTreeNode node) {
        if (node.right != nil) {
            return minimum(node.right);
        }
        RedBlackTreeNode parent = node.parent;
        while (parent != nil && node == parent.right) {
            node = parent;
            parent = parent.parent;
        }
        return parent;
    }

    private void rotateLeft(RedBlackTreeNode x) {
        RedBlackTreeNode y = x.right;
        x.right = y.left;
        if (y.left != nil) {
            y.left.parent = x;
        }
        y.parent = x.parent;
        if (x.parent == nil) {
            root = y;
        } else if (x == x.parent.left) {
            x.parent.left = y;
        } else {
            x.parent.right = y;
        }
        y.left = x;
        x.parent = y;
    }

    private void rotateRight(RedBlackTreeNode y) {
        RedBlackTreeNode x = y.left;
        y.left = x.right;
        if (x.right != nil) {
            x.right.parent = y;
        }
        x.parent = y.parent;
        if (y.parent == nil) {
            root = x;
        } else if (y == y.parent.left) {
            y.parent.left = x;
        } else {
            y.parent.right = x;
        }
        x.right = y;
        y.parent = x;
    }

    public void insert(RedBlackTreeNode z) {
        RedBlackTreeNode y = nil;
        RedBlackTreeNode x = root;

        while (x != nil) {
            y = x;
            int cmp = ((String) z.key).compareTo((String) x.key);
            if (cmp < 0) {
                x = x.left;
            } else if (cmp > 0) {
                x = x.right;
            } else {
                x.value = z.value; // replace value
                return;
            }
        }

        z.parent = y;
        if (y == nil) {
            root = z;
        } else if (((String) z.key).compareTo((String) y.key) < 0) {
            y.left = z;
        } else {
            y.right = z;
        }
        z.left = z.right = nil;
        z.color = RED;

        insertFixup(z);
    }

    private void insertFixup(RedBlackTreeNode z) {
        while (color(z.parent) == RED) {
            if (z.parent == z.parent.parent.left) {
                RedBlackTreeNode y = z.parent.parent.right;
                if (color(y) == RED) {
                    z.parent.color = BLACK;
                    y.color = BLACK;
                    z.parent.parent.color = RED;
                    z = z.parent.parent;
                } else {
                    if (z == z.parent.right) {
                        z = z.parent;
                        rotateLeft(z);
                    }
                    z.parent.color = BLACK;
                    z.parent.parent.color = RED;
                    rotateRight(z.parent.parent);
                }
            } else {
                RedBlackTreeNode y = z.parent.parent.left;
                if (color(y) == RED) {
                    z.parent.color = BLACK;
                    y.color = BLACK;
                    z.parent.parent.color = RED;
                    z = z.parent.parent;
                } else {
                    if (z == z.parent.left) {
                        z = z.parent;
                        rotateRight(z);
                    }
                    z.parent.color = BLACK;
                    z.parent.parent.color = RED;
                    rotateLeft(z.parent.parent);
                }
            }
        }
        root.color = BLACK;
    }

    public void delete(RedBlackTreeNode z) {
        RedBlackTreeNode y = z;
        RedBlackTreeNode x;
        int yOriginalColor = y.color;

        if (z.left == nil) {
            x = z.right;
            transplant(z, z.right);
        } else if (z.right == nil) {
            x = z.left;
            transplant(z, z.left);
        } else {
            y = minimum(z.right);
            yOriginalColor = y.color;
            x = y.right;
            if (y.parent == z) {
                x.parent = y;
            } else {
                transplant(y, y.right);
                y.right = z.right;
                y.right.parent = y;
            }
            transplant(z, y);
            y.left = z.left;
            y.left.parent = y;
            y.color = z.color;
        }

        if (yOriginalColor == BLACK) {
            deleteFixup(x);
        }
    }

    private void deleteFixup(RedBlackTreeNode x) {
        while (x != root && color(x) == BLACK) {
            if (x == x.parent.left) {
                RedBlackTreeNode w = x.parent.right;
                if (color(w) == RED) {
                    w.color = BLACK;
                    x.parent.color = RED;
                    rotateLeft(x.parent);
                    w = x.parent.right;
                }
                if (color(w.left) == BLACK && color(w.right) == BLACK) {
                    w.color = RED;
                    x = x.parent;
                } else {
                    if (color(w.right) == BLACK) {
                        w.left.color = BLACK;
                        w.color = RED;
                        rotateRight(w);
                        w = x.parent.right;
                    }
                    w.color = x.parent.color;
                    x.parent.color = BLACK;
                    w.right.color = BLACK;
                    rotateLeft(x.parent);
                    x = root;
                }
            } else {
                RedBlackTreeNode w = x.parent.left;
                if (color(w) == RED) {
                    w.color = BLACK;
                    x.parent.color = RED;
                    rotateRight(x.parent);
                    w = x.parent.left;
                }
                if (color(w.left) == BLACK && color(w.right) == BLACK) {
                    w.color = RED;
                    x = x.parent;
                } else {
                    if (color(w.left) == BLACK) {
                        w.right.color = BLACK;
                        w.color = RED;
                        rotateLeft(w);
                        w = x.parent.left;
                    }
                    w.color = x.parent.color;
                    x.parent.color = BLACK;
                    w.left.color = BLACK;
                    rotateRight(x.parent);
                    x = root;
                }
            }
        }
        x.color = BLACK;
    }

    private void transplant(RedBlackTreeNode u, RedBlackTreeNode v) {
        if (u.parent == nil) {
            root = v;
        } else if (u == u.parent.left) {
            u.parent.left = v;
        } else {
            u.parent.right = v;
        }
        v.parent = u.parent;
    }

    public RedBlackTreeNode search(Object key) {
        RedBlackTreeNode current = root;
        while (current != nil && !current.key.equals(key)) {
            if (((String) key).compareTo((String) current.key) < 0) {
                current = current.left;
            } else {
                current = current.right;
            }
        }
        return current;
    }

    protected void inorderWalk(RedBlackTreeNode node) {
        if (node != nil) {
            inorderWalk(node.left);
            System.out.println("Key: " + node.key + ", Value: " + node.value);
            inorderWalk(node.right);
        }
    }

    public void walk() {
        inorderWalk(getRoot());
    }
}
