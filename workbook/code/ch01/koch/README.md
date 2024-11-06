
## Koch snowflakes

### For beginners

1. Basic line drawing with recursion:
- Objective: Implement the Koch curve, but only for a single line segment.
- Exercise: Start with a line segment and recursively apply the Koch fractal rule to divide it into smaller segments, gradually creating a jagged line. This helps to understand recursion through visual feedback.
- Goal: Print the coordinates at each recursive step or plot them with a simple plotting library.

2. Tracing the recursive calls:
- Objective: Understand the recursion depth and number of calls.
- Exercise: Trace the recursive calls and print each level of recursion, possibly with indentation to show hierarchy.
- Goal: Visualize how many times the function calls itself, and discuss the memory usage and computational cost of recursion.

3. Drawing the snowflake with simple loops (in book):
- Objective: Introduce basic loops and iteration before diving into recursion.
- Exercise: Get the first the points for one iteration of a Koch snowflake and draw the entire snowflake using for loops.
- Goal: Build an understanding of how symmetry (120-degree rotation) works in the snowflake.
- Code: [koch.py](koch.py)

4. Counting segments in each teration:
- Objective: Calculate the growth in complexity.
- Exercise: Count how many line segments are created at each recursive depth.
- Goal: Show how recursion can exponentially increase the number of segments and discuss how this impacts the complexity of fractals.


### For non-beginners

1. Animating the Koch snowflake:
- Objective: Create a dynamic visualization of the snowflake's growth with each recursion.
- Exercise: Use a library like matplotlib or pygame to draw the Koch snowflake in real-time, updating the display as each recursion level is added. Or use JavaScript and Canvas.
- Goal: Explore practical aspects of rendering, animation, and performance issues with recursive drawings.

2. Optimising recursion with memoization:
- Objective: Reduce redundant calculations.
- Exercise: Implement memoization (caching) to store previously computed line segments, reusing them if the recursion path duplicates work.
- Goal: Understand optimisation techniques in recursion and when they're applicable.

3. Koch snowflake with dynamic levels of recursion (in book):
- Objective: Interact with recursion levels in real-time.
- Exercise: Create a program that allows users to input the recursion depth (e.g., from 1 to 6) to adjust the level of detail in the snowflake.
- Goal: Demonstrate how recursion depth affects complexity, and help students develop user interaction within recursive programs.
- Code: [JavaScript](koch.html).

4. Drawing the snowflake in 3D:
- Objective: Extend the fractal concept to three dimensions.
- Exercise: Implement a 3D Koch snowflake variant, where each side of the snowflake branches out into three-dimensional space.
- Goal: Introduce the challenges of 3D space transformations, while reinforcing recursive thinking with a more complex visualization.

5. Writing a PPM image generator for any fractal depth:
- Objective: Understand file I/O and image generation using recursion.
- Exercise: Expand on the Koch snowflake by writing a program that outputs the fractal at various recursion depths as a PPM image.
- Goal: Practice generating visual files programmatically and understand how recursion can directly control pixel-level output.

6. Comparing Recursive and Iterative Approaches:
- Objective: Introduce alternative recursive implementations.
- Exercise: Implement both a recursive and an iterative version of the Koch curve, comparing performance and memory usage.
- Goal: Discuss to both methods, on where recursion is advantageous and when iteration might be more efficient.

7. Calculating the snowflake's fractal dimension:
- Objective: Explore mathematical properties of fractals.
- Exercise: Explore through calculating the fractal dimension of the Koch snowflake by analyzing how the length and complexity increase with each iteration.
- Goal: Connect programming to mathematical theory and introduce concepts like self-similarity and fractal dimension.

These exercises should encourage both groups to apply recursion in creative and analytical ways, deepening understanding of recursion's capabilities and its application in real-world computing.
