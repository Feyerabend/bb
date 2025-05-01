
public class Main {
    public static void main(String[] args) {
        RedBlackTree b = new RedBlackTree();

        // Insert nodes
        b.insert(new RedBlackTreeNode("Zeus", "Thunder"));
        b.insert(new RedBlackTreeNode("Hades", "Underworld"));
        b.insert(new RedBlackTreeNode("Poseidon", "Sea"));
        b.insert(new RedBlackTreeNode("Hermes", "Messenger"));
        b.insert(new RedBlackTreeNode("Demeter", "Harvest"));
        b.insert(new RedBlackTreeNode("Dionysus", "Wine"));
        b.insert(new RedBlackTreeNode("Ares", "War"));
        b.insert(new RedBlackTreeNode("Artemis", "Hunt"));
        b.insert(new RedBlackTreeNode("Hephaestus", "Forge"));

        // Inorder traversal
        System.out.println("Walk:");
        b.walk();
        System.out.println();

        // Search for a key
        RedBlackTreeNode node = b.search((Object)"Ares");
        if (node != b.nil) {
            System.out.println("Found Ares: " + node.value);
        } else {
            System.out.println("Ares not found");
        }

        // Delete a node
        b.delete(node);
        System.out.println("After deleting Ares:");
        System.out.println("Walk:");
        b.walk();

        RedBlackTreeNode t = new RedBlackTreeNode("Hephaestus", "Poff!");
        b.insert(t);
        System.out.println();
        b.walk();

    }
}

