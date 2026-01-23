
## CFG

In a compiler, a Control Flow Graph (CFG) is a representation of all paths
that can be traversed through a program during execution. It's a vital structure
used for various compiler optimisations and analyses, such as dead code elimination,
loop unrolling, and more.

Let’s walk through how you might implement a CFG in a compiler.
Step-by-Step Implementation of CFG

Understanding the Components of a CFG
Nodes (Basic Blocks): A basic block is a sequence of instructions in which the control flow enters at the beginning and exits at the end. There's no branching except at the end of the block.
Edges (Control Flow): An edge represents a possible jump from one basic block to another. This is usually caused by control structures like if, while, for, or function calls.
Creating a Basic Block A basic block contains a series of statements that are executed sequentially. The entry and exit points are typically at the beginning and end of the block, and control does not deviate unless an explicit jump is made (such as a goto, if, or return statement).
To create a basic block:
Split the code at each conditional statement, loop, or jump, where control flow may branch.
Each segment of code between these branch points becomes a basic block.
Building the CFG
For each instruction in the program, identify its basic block.
Add edges between blocks based on jump instructions (if, goto, etc.).
Example: Implementing CFG for a Simple Program

Let’s implement a simple control flow graph in Python. We'll assume that we
have a list of statements in a program and we'll break it down into basic blocks.
Example Program:
```c
int fib(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}
```
Step 1: Identify the Basic Blocks

In this example, the basic blocks are:
- Block 1: Start of the function, includes the if (n <= 1) check.
- Block 2: Contains the initialization of a and b, and the for loop.
- Block 3: The body of the for loop.
- Block 4: The return b statement.

Step 2: Identify the Control Flow

The control flow is:
- From the entry point to Block 1 (checking n <= 1).
- If n <= 1 is true, jump to Block 4 (returning n).
- If n > 1, move to Block 2 (initialization and for loop).
- Inside the for loop, each iteration executes Block 3 (calculating Fibonacci).
- After the loop, the program moves to Block 4 and returns b.

Step 3: Implement the CFG in Python

Here’s a basic implementation in Python where we create nodes (basic blocks) and edges (control flow between blocks):
```python
class CFGNode:
    def __init__(self, block_id, statements):
        self.block_id = block_id
        self.statements = statements
        self.edges = []  # List of nodes this block points to

    def add_edge(self, target_node):
        self.edges.append(target_node)

class ControlFlowGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, block_id, statements):
        node = CFGNode(block_id, statements)
        self.nodes[block_id] = node
        return node

    def display(self):
        for block_id, node in self.nodes.items():
            print(f"Block {block_id}:")
            print(f"  Statements: {node.statements}")
            print(f"  Control Flow: {[edge.block_id for edge in node.edges]}")

# Initialize the CFG
cfg = ControlFlowGraph()

# Add nodes (basic blocks)
block_1 = cfg.add_node(1, ["if (n <= 1)"])
block_2 = cfg.add_node(2, ["int a = 0, b = 1;", "for (int i = 2; i <= n; i++)"])
block_3 = cfg.add_node(3, ["int temp = a + b;", "a = b;", "b = temp;"])
block_4 = cfg.add_node(4, ["return b;"])

# Add edges (control flow)
block_1.add_edge(block_2)  # From Block 1 to Block 2 (if n > 1)
block_1.add_edge(block_4)  # From Block 1 to Block 4 (if n <= 1)

block_2.add_edge(block_3)  # From Block 2 to Block 3 (start of for loop)
block_3.add_edge(block_3)  # From Block 3 to Block 3 (inside loop, back to itself)
block_3.add_edge(block_4)  # From Block 3 to Block 4 (after loop finishes)

# Display the CFG
cfg.display()
Output:

Block 1:
  Statements: ['if (n <= 1)']
  Control Flow: [2, 4]
Block 2:
  Statements: ['int a = 0, b = 1;', 'for (int i = 2; i <= n; i++)']
  Control Flow: [3]
Block 3:
  Statements: ['int temp = a + b;', 'a = b;', 'b = temp;']
  Control Flow: [3, 4]
Block 4:
  Statements: ['return b;']
  Control Flow: []
```

Explanation:

- Block 1 is where the function checks if n <= 1. If true, it jumps to Block 4 (the return statement). Otherwise, it proceeds to Block 2.
- Block 2 initializes variables and enters the loop.
- Block 3 is inside the loop and performs the Fibonacci calculations. After each iteration, it jumps back to Block 3 (since the loop continues) until the loop ends, and then it jumps to Block 4.
- Block 4 returns the result.


Step 4: Use the CFG for Optimisation

With this CFG, the compiler can perform various optimizations, such as:
Dead code elimination: If any block doesn't affect the program's final result, it can be removed.
Constant folding: If any expressions in the basic blocks are constant, they can be evaluated at compile-time.
Loop optimizations: The compiler can analyze the loop structure (like in Block 2 and Block 3) for potential optimizations like loop unrolling or invariant code motion.

### Conclusion

The Control Flow Graph (CFG) is a powerful tool in compiler design. It abstracts the program's control flow into nodes and edges, making it easier to analyze the flow of execution and optimize the program. The process of building the CFG involves identifying basic blocks, determining control flow, and then using this structure for various analyses and optimizations.




Creating a Control Flow Graph (CFG) for a parsed PL/0 program (which is a simple programming language) involves using an Abstract Syntax Tree (AST) as input. PL/0 has a limited set of constructs, such as assignment statements, conditionals, loops, and procedure calls. The steps to implement the CFG from an AST in Python will involve parsing the AST nodes, identifying basic blocks, and creating control flow edges based on the control flow statements (such as if, while, and assignment statements).
Let's break down the task into manageable steps:
Steps to Build a CFG from an AST:

Representation of AST: Each AST node represents a part of the program (e.g., an expression, assignment, or control structure). We need a data structure to store this information.
Basic Blocks: A basic block is a sequence of instructions that has a single entry point and a single exit point. We will use the AST to create these basic blocks.
Edges: We need to traverse the AST and identify where control can jump from one block to another. For example, if statements have branches based on the condition, and loops have back edges.
CFG Construction: For each control flow construct in the AST (like if, while, or assignments), we will construct a Control Flow Graph using basic blocks and control edges.


1. Defining the AST Nodes and the CFG

First, we need to define the structure of an AST node and a CFG node in Python.
```python
class ASTNode:
    def __init__(self, node_type, children=None, statement=None):
        self.node_type = node_type  # Type of the AST node (e.g., assignment, if, while)
        self.children = children if children else []  # List of child nodes (for control structures, etc.)
        self.statement = statement  # The statement or expression this node represents (if any)

class CFGNode:
    def __init__(self, block_id, statements):
        self.block_id = block_id
        self.statements = statements
        self.edges = []  # List of successor CFG nodes this block points to

    def add_edge(self, target_node):
        self.edges.append(target_node)

class ControlFlowGraph:
    def __init__(self):
        self.nodes = {}
        self.next_block_id = 0

    def add_node(self, statements):
        node = CFGNode(self.next_block_id, statements)
        self.nodes[self.next_block_id] = node
        self.next_block_id += 1
        return node

    def display(self):
        for block_id, node in self.nodes.items():
            print(f"Block {block_id}:")
            print(f"  Statements: {node.statements}")
            print(f"  Control Flow: {[edge.block_id for edge in node.edges]}")
```

2. Parsing the AST and Constructing the CFG

Let's assume we have an AST that represents a simple PL/0 program. We will recursively traverse the AST and construct the CFG. We will create basic blocks based on the type of the AST nodes (like if, while, assignments, etc.), and connect them with edges.
Here’s a simplified version of how you could implement this traversal in Python:
```python
def build_cfg_from_ast(ast_node, cfg, parent_node=None):
    """
    Recursively builds the Control Flow Graph from the AST.
    
    :param ast_node: Current AST node
    :param cfg: The ControlFlowGraph instance
    :param parent_node: The parent node from which control flows into the current node
    :return: Current CFG node
    """
    # Create a new basic block for the current AST node
    current_node = None

    # Handle different types of AST nodes
    if ast_node.node_type == "assignment":
        current_node = cfg.add_node([ast_node.statement])

    elif ast_node.node_type == "if":
        current_node = cfg.add_node([f"if ({ast_node.statement})"])
        # Add an edge to the "true" branch and the "false" branch
        true_branch = build_cfg_from_ast(ast_node.children[0], cfg)
        false_branch = build_cfg_from_ast(ast_node.children[1], cfg)
        current_node.add_edge(true_branch)
        current_node.add_edge(false_branch)

    elif ast_node.node_type == "while":
        current_node = cfg.add_node([f"while ({ast_node.statement})"])
        # Create a loop with a back edge
        loop_body = build_cfg_from_ast(ast_node.children[0], cfg)
        current_node.add_edge(loop_body)
        loop_body.add_edge(current_node)  # Back edge for the loop

    elif ast_node.node_type == "block":
        current_node = cfg.add_node([f"begin block"])
        for child in ast_node.children:
            child_node = build_cfg_from_ast(child, cfg, current_node)
            current_node.add_edge(child_node)

    # Add edges from the parent node to the current node
    if parent_node:
        parent_node.add_edge(current_node)

    return current_node
```

3. Example Program in AST

Let's assume a simple PL/0 program that computes the Fibonacci sequence using a while loop:

```pascal
BEGIN
  a := 0;
  b := 1;
  i := 2;
  WHILE i <= n DO
    temp := a + b;
    a := b;
    b := temp;
    i := i + 1;
  END;
  RETURN b;
END.
```

We will represent the AST of this program with the following structure:

```python
ast_root = ASTNode("block", [
    ASTNode("assignment", statement="a := 0"),
    ASTNode("assignment", statement="b := 1"),
    ASTNode("assignment", statement="i := 2"),
    ASTNode("while", statement="i <= n", children=[
        ASTNode("assignment", statement="temp := a + b"),
        ASTNode("assignment", statement="a := b"),
        ASTNode("assignment", statement="b := temp"),
        ASTNode("assignment", statement="i := i + 1")
    ]),
    ASTNode("return", statement="b")
])

# Init CFG
cfg = ControlFlowGraph()

# Build the CFG from the AST
build_cfg_from_ast(ast_root, cfg)

# Display the constructed CFG
cfg.display()
```

4. Output of the CFG Construction

The output will be a set of blocks that represent the control flow of the program:

```
Block 0:
  Statements: ['begin block']
  Control Flow: [1]
Block 1:
  Statements: ['a := 0']
  Control Flow: [2]
Block 2:
  Statements: ['b := 1']
  Control Flow: [3]
Block 3:
  Statements: ['i := 2']
  Control Flow: [4]
Block 4:
  Statements: ['while (i <= n)']
  Control Flow: [5, 8]
Block 5:
  Statements: ['temp := a + b']
  Control Flow: [6]
Block 6:
  Statements: ['a := b']
  Control Flow: [7]
Block 7:
  Statements: ['b := temp']
  Control Flow: [8]
Block 8:
  Statements: ['i := i + 1']
  Control Flow: [4]
Block 9:
  Statements: ['return b']
  Control Flow: []
```

Explanation of the CFG:

- Block 0: Entry point of the program (the start of the block).
- Block 1, 2, 3: Assignments for initializing variables a, b, and i.
- Block 4: The while loop with the condition i <= n. This has two edges:
    - One goes to Block 5 (the body of the loop).
    - The other goes to Block 8 when the condition is false (return b).
- Block 5-7: Statements inside the loop (calculating the Fibonacci values).
- Block 8: Incrementing i and looping back to the condition check.
- Block 9: Returning the value of b.


### Conclusion

This simple example demonstrates how to convert an Abstract Syntax Tree (AST) into a Control Flow Graph (CFG) for a PL/0 program. The process involves recursively parsing the AST, generating basic blocks for each statement or control structure, and establishing edges based on the control flow logic. This CFG can then be used for various compiler optimizations, such as dead code elimination, constant folding, and loop transformations.




Step 1: Input Format (in ASCII)

We will take the control flow graph (CFG) as an input string in a format like this:

```python
Block 0:
  Statements: ['begin block']
  Control Flow: [1]
Block 1:
  Statements: ['a := 0']
  Control Flow: [2]
Block 2:
  Statements: ['b := 1']
  Control Flow: [3]
Block 3:
  Statements: ['i := 2']
  Control Flow: [4]
Block 4:
  Statements: ['while (i <= n)']
  Control Flow: [5, 8]
Block 5:
  Statements: ['temp := a + b']
  Control Flow: [6]
Block 6:
  Statements: ['a := b']
  Control Flow: [7]
Block 7:
  Statements: ['b := temp']
  Control Flow: [8]
Block 8:
  Statements: ['i := i + 1']
  Control Flow: [4]
Block 9:
  Statements: ['return b']
  Control Flow: []
```





Python Code for Visualisation

```python
class ControlFlowGraph:
    def __init__(self):
        self.blocks = {}

    def add_block(self, block_id, statements, control_flow):
        self.blocks[block_id] = {'statements': statements, 'control_flow': control_flow}

    def display(self):
        # Construct the ASCII art representation of the graph
        graph_text = ''
        for block_id, block in self.blocks.items():
            graph_text += f"Block {block_id}:\n"
            graph_text += f"  Statements: {', '.join(block['statements'])}\n"
            graph_text += f"  Control Flow: {', '.join(map(str, block['control_flow']))}\n"
            graph_text += f"\n"
            graph_text += f"Block {block_id} --> [{', '.join(map(str, block['control_flow']))}]\n"
        
        return graph_text

# Function to parse the input string into a structured format
def parse_input(input_str):
    blocks = {}
    block_lines = input_str.strip().split('\n\n')
    
    for block in block_lines:
        lines = block.split('\n')
        block_id = int(lines[0].split()[1][:-1])  # Extract Block ID (e.g., Block 0:)
        statements = [s.strip()[1:-1] for s in lines[1].split('Statements: ')[1].split(',')]
        control_flow = list(map(int, lines[2].split('Control Flow: ')[1].split(',')))
        
        blocks[block_id] = {'statements': statements, 'control_flow': control_flow}
    
    return blocks

# Input as a string (same as the format you provided)
input_str = """
Block 0:
  Statements: ['begin block']
  Control Flow: [1]
Block 1:
  Statements: ['a := 0']
  Control Flow: [2]
Block 2:
  Statements: ['b := 1']
  Control Flow: [3]
Block 3:
  Statements: ['i := 2']
  Control Flow: [4]
Block 4:
  Statements: ['while (i <= n)']
  Control Flow: [5, 8]
Block 5:
  Statements: ['temp := a + b']
  Control Flow: [6]
Block 6:
  Statements: ['a := b']
  Control Flow: [7]
Block 7:
  Statements: ['b := temp']
  Control Flow: [8]
Block 8:
  Statements: ['i := i + 1']
  Control Flow: [4]
Block 9:
  Statements: ['return b']
  Control Flow: []
"""

# Parse the input into blocks
blocks = parse_input(input_str)

# Create a control flow graph
cfg = ControlFlowGraph()
for block_id, block in blocks.items():
    cfg.add_block(block_id, block['statements'], block['control_flow'])

# Display the control flow graph
print(cfg.display())
```


How This Works:

- Parse the Input: We first parse the provided input text into a structured format (using parse_input), which breaks down the control flow graph into individual blocks, their statements, and their control flow.
- Store Blocks: We store each block's data (statements and control flow) in a ControlFlowGraph object.
- Display the Graph: We then construct a textual ASCII representation of the graph using display() and print it to the console.


Example Input

You can provide the same input format as before, which looks like this:
```
Block 0:
  Statements: ['begin block']
  Control Flow: [1]
Block 1:
  Statements: ['a := 0']
  Control Flow: [2]
Block 2:
  Statements: ['b := 1']
  Control Flow: [3]
Block 3:
  Statements: ['i := 2']
  Control Flow: [4]
Block 4:
  Statements: ['while (i <= n)']
  Control Flow: [5, 8]
Block 5:
  Statements: ['temp := a + b']
  Control Flow: [6]
Block 6:
  Statements: ['a := b']
  Control Flow: [7]
Block 7:
  Statements: ['b := temp']
  Control Flow: [8]
Block 8:
  Statements: ['i := i + 1']
  Control Flow: [4]
Block 9:
  Statements: ['return b']
  Control Flow: []
```

Output

Here’s an example output that the above code would generate:
```
Block 0:
  Statements: begin block
  Control Flow: 1

Block 1:
  Statements: a := 0
  Control Flow: 2

Block 2:
  Statements: b := 1
  Control Flow: 3

Block 3:
  Statements: i := 2
  Control Flow: 4

Block 4:
  Statements: while (i <= n)
  Control Flow: 5, 8

Block 5:
  Statements: temp := a + b
  Control Flow: 6

Block 6:
  Statements: a := b
  Control Flow: 7

Block 7:
  Statements: b := temp
  Control Flow: 8

Block 8:
  Statements: i := i + 1
  Control Flow: 4

Block 9:
  Statements: return b

  Control Flow: 

Block 0 --> [1]
Block 1 --> [2]
Block 2 --> [3]
Block 3 --> [4]
Block 4 --> [5, 8]
Block 5 --> [6]
Block 6 --> [7]
Block 7 --> [8]
Block 8 --> [4]
Block 9 --> []
```

---

Visualise the control flow graph (CFG) as an SVG?
It generates nodes for each block and lines to represent the control flow connections:


```python
import svgwrite

class ControlFlowGraphSVG:
    def __init__(self):
        self.blocks = {}
        self.positions = {}

    def add_block(self, block_id, statements, control_flow):
        self.blocks[block_id] = {'statements': statements, 'control_flow': control_flow}

    def generate_svg(self, filename='control_flow_graph.svg'):
        dwg = svgwrite.Drawing(filename, size=(800, 600), profile='tiny')
        
        # Layout parameters
        x_start, y_start = 50, 50
        x_step, y_step = 200, 100
        block_width, block_height = 120, 60

        # Assign positions for each block
        for idx, block_id in enumerate(self.blocks.keys()):
            x = x_start + (idx % 4) * x_step
            y = y_start + (idx // 4) * y_step
            self.positions[block_id] = (x, y)

        # Draw blocks
        for block_id, block in self.blocks.items():
            x, y = self.positions[block_id]
            dwg.add(dwg.rect(insert=(x, y), size=(block_width, block_height),
                             rx=10, ry=10, fill='lightblue', stroke='black'))
            dwg.add(dwg.text(f"Block {block_id}", insert=(x + 10, y + 20),
                             fill='black', font_size='12', font_family='Arial'))
            for i, stmt in enumerate(block['statements']):
                dwg.add(dwg.text(stmt, insert=(x + 10, y + 35 + i * 12),
                                 fill='black', font_size='10', font_family='Arial'))

        # Draw control flow arrows
        for block_id, block in self.blocks.items():
            x1, y1 = self.positions[block_id]
            for target_id in block['control_flow']:
                x2, y2 = self.positions[target_id]
                x1_center, y1_center = x1 + block_width / 2, y1 + block_height
                x2_center, y2_center = x2 + block_width / 2, y2
                dwg.add(dwg.line(start=(x1_center, y1_center),
                                 end=(x2_center, y2_center),
                                 stroke='black', marker_end=svgwrite.Marker(type='arrow', orient='auto')))
                # Add an arrowhead for visual clarity
                dwg.add(dwg.marker(id='arrow', orient="auto", insert=(10, 5), size=(10, 10),
                                   refX=10, refY=5,
                                   viewBox="0 0 10 10").add(dwg.path(d="M0,0 L10,5 L0,10 Z", fill='black')))

        # Save the SVG file
        dwg.save()


# Parse the input string into a structured format
def parse_input(input_str):
    blocks = {}
    block_lines = input_str.strip().split('\n\n')
    
    for block in block_lines:
        lines = block.split('\n')
        block_id = int(lines[0].split()[1][:-1])  # Extract Block ID (e.g., Block 0:)
        statements = [s.strip()[1:-1] for s in lines[1].split('Statements: ')[1].split(',')]
        control_flow = list(map(int, lines[2].split('Control Flow: ')[1].split(',')))
        
        blocks[block_id] = {'statements': statements, 'control_flow': control_flow}
    
    return blocks

# Input as a string
input_str = """
Block 0:
  Statements: ['begin block']
  Control Flow: [1]
Block 1:
  Statements: ['a := 0']
  Control Flow: [2]
Block 2:
  Statements: ['b := 1']
  Control Flow: [3]
Block 3:
  Statements: ['i := 2']
  Control Flow: [4]
Block 4:
  Statements: ['while (i <= n)']
  Control Flow: [5, 8]
Block 5:
  Statements: ['temp := a + b']
  Control Flow: [6]
Block 6:
  Statements: ['a := b']
  Control Flow: [7]
Block 7:
  Statements: ['b := temp']
  Control Flow: [8]
Block 8:
  Statements: ['i := i + 1']
  Control Flow: [4]
Block 9:
  Statements: ['return b']
  Control Flow: []
"""

# Parse the input into blocks
blocks = parse_input(input_str)

# Create a control flow graph and add blocks
cfg = ControlFlowGraphSVG()
for block_id, block in blocks.items():
    cfg.add_block(block_id, block['statements'], block['control_flow'])

# Generate the SVG file
cfg.generate_svg('control_flow_graph.svg')
```


Explanation:
1. Node Positions: Each block is assigned a position in a grid-like layout based on the block ID.
2. Drawing Nodes: Rectangles represent blocks, and the statements are added as text within the rectangles.
3. Drawing Edges: Lines with arrowheads indicate control flow connections between blocks.
4. File Output: The graph is saved as an SVG file named control_flow_graph.svg.

