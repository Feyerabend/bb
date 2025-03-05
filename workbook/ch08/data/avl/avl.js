
class Node {
    constructor(value) {
        this.value = value;
        this.left = null;
        this.right = null;
        this.height = 1;
    }
}

class AVLTree {
    constructor() {
        this.root = null;
    }

    getHeight(node) {
        return node ? node.height : 0;
    }

    updateHeight(node) {
        node.height = Math.max(this.getHeight(node.left), this.getHeight(node.right)) + 1;
    }

    getBalanceFactor(node) {
        return node ? this.getHeight(node.left) - this.getHeight(node.right) : 0;
    }

    rotateRight(y) {
        const x = y.left;
        const T2 = x.right;

        x.right = y;
        y.left = T2;

        this.updateHeight(y);
        this.updateHeight(x);

        return x;
    }

    rotateLeft(x) {
        const y = x.right;
        const T2 = y.left;

        y.left = x;
        x.right = T2;

        this.updateHeight(x);
        this.updateHeight(y);

        return y;
    }

    insert(node, value) {
        if (!node) return new Node(value);

        if (value < node.value) {
            node.left = this.insert(node.left, value);
        } else if (value > node.value) {
            node.right = this.insert(node.right, value);
        } else {
            return node; // dups not allowed
        }

        this.updateHeight(node);
        return this.rebalance(node);
    }

    delete(node, value) {
        if (!node) return null;

        if (value < node.value) {
            node.left = this.delete(node.left, value);
        } else if (value > node.value) {
            node.right = this.delete(node.right, value);
        } else {
            if (!node.left || !node.right) {
                node = node.left || node.right; // if only one child (or none)
            } else {
                const temp = this.findMin(node.right);
                node.value = temp.value;
                node.right = this.delete(node.right, temp.value);
            }
        }

        if (!node) return null; // if tree empty

        this.updateHeight(node);
        return this.rebalance(node);
    }

    rebalance(node) {
        const balance = this.getBalanceFactor(node);

        // Left Heavy (LL or LR)
        if (balance > 1) {
            if (this.getBalanceFactor(node.left) < 0) {
                node.left = this.rotateLeft(node.left); // LR case
            }
            return this.rotateRight(node); // LL case
        }

        // Right Heavy (RR or RL)
        if (balance < -1) {
            if (this.getBalanceFactor(node.right) > 0) {
                node.right = this.rotateRight(node.right); // RL case
            }
            return this.rotateLeft(node); // RR case
        }

        return node;
    }

    findMin(node) {
        while (node.left) {
            node = node.left;
        }
        return node;
    }

    insertValue(value) {
        this.root = this.insert(this.root, value);
    }

    deleteValue(value) {
        this.root = this.delete(this.root, value);
    }

    visualize() {
        const container = document.getElementById('tree-container');
        container.innerHTML = '';

        if (!this.root) return;

        // maximum depth of the tree
        const maxDepth = this.getHeight(this.root);

        // horizontal spacing based on depth
        const baseOffsetX = (window.innerWidth / Math.pow(2, maxDepth)) * 0.8;
        const baseOffsetY = 80;

        this._visualizeNode(this.root, container, window.innerWidth / 2, 50, baseOffsetX, baseOffsetY);
    }

    _visualizeNode(node, parentElement, x, y, offsetX, offsetY) {
        if (!node) return;

        const nodeElement = document.createElement('div');
        nodeElement.className = 'node';
        nodeElement.textContent = node.value;
        nodeElement.style.left = `${x}px`;
        nodeElement.style.top = `${y}px`;
        parentElement.appendChild(nodeElement);

        if (node.left) {
            const leftX = x - offsetX;
            const leftY = y + offsetY;
            this._drawLine(x + 20, y + 40, leftX + 20, leftY, parentElement);
            this._visualizeNode(node.left, parentElement, leftX, leftY, offsetX / 2, offsetY);
        }

        if (node.right) {
            const rightX = x + offsetX;
            const rightY = y + offsetY;
            this._drawLine(x + 20, y + 40, rightX + 20, rightY, parentElement);
            this._visualizeNode(node.right, parentElement, rightX, rightY, offsetX / 2, offsetY);
        }
    }

    _drawLine(x1, y1, x2, y2, parentElement) {
        const line = document.createElement('div');
        line.className = 'line';
        const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);
        line.style.width = `${length}px`;
        line.style.transform = `rotate(${angle}deg)`;
        line.style.left = `${x1}px`;
        line.style.top = `${y1}px`;
        parentElement.appendChild(line);
    }
}

const avlTree = new AVLTree();

function addNode() {
    const value = parseInt(document.getElementById('input').value);
    if (!isNaN(value)) {
        avlTree.root = avlTree.insert(avlTree.root, value);
        avlTree.visualize();
    }
}

function deleteNode() {
    const value = parseInt(document.getElementById('input').value);
    if (!isNaN(value)) {
        avlTree.root = avlTree.delete(avlTree.root, value);
        avlTree.visualize();
    }
}

// Zoom and Pan
let scale = 1;
let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let startX, startY;

const treeContainer = document.getElementById('tree-container');

treeContainer.addEventListener('wheel', (e) => {
    e.preventDefault();
    scale += e.deltaY * -0.01;
    scale = Math.min(Math.max(0.5, scale), 2); // scale between 0.5x and 2x
    treeContainer.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
});

treeContainer.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX - offsetX;
    startY = e.clientY - offsetY;
});

treeContainer.addEventListener('mousemove', (e) => {
    if (isDragging) {
        offsetX = e.clientX - startX;
        offsetY = e.clientY - startY;
        treeContainer.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
    }
});

treeContainer.addEventListener('mouseup', () => {
    isDragging = false;
});

treeContainer.addEventListener('mouseleave', () => {
    isDragging = false;
});

function zoomIn() {
    scale += 0.1;
    scale = Math.min(scale, 2); // max zoom 2x
    treeContainer.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
}

function zoomOut() {
    scale -= 0.1;
    scale = Math.max(scale, 0.5); // min zoom 0.5x
    treeContainer.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
}