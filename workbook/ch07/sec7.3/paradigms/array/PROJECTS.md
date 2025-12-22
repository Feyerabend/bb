
## Projects

> [!NOTE]
> *You might have to change the `APLArray` quite a bit to get working for any practical use, as it hasn't been thoroughly tested for any serious extension.*


### 1. Build a Domain-Specific Language (DSL) for Array Operations

Create a small DSL that allows users to write concise, APL-like expressions for array operations.
This project will involve designing a parser and interpreter for the DSL.


#### Steps:
1. Define the syntax for the DSL (e.g., inspired by APL symbols like `⍴`, `⌽`, `⍋`).
2. Implement a lexer and parser to convert DSL expressions into Python code.
3. Use the `APLArray` class as the backend for executing the operations.
4. Add support for common array operations like reshaping, sorting, and reductions.


#### Example DSL:
```apl
# Reshape an array to 2x3
array ← 1 2 3 4 5 6
array ⍴ 2 3

# Reverse an array
⌽ array

# Sort an array in ascending order
⍋ array
```

#### Tools:
- Use a parsing library like [Lark](https://github.com/lark-parser/lark)
   or [PLY](https://github.com/dabeaz/ply) for building the DSL.
- Map DSL operations to `APLArray` methods.


### 2. Create an Interactive Array Calculator
Build an interactive calculator that allows users to perform array operations using a command-line interface (CLI) or a graphical user interface (GUI).

#### Features:
- Support for basic arithmetic operations (addition, subtraction, multiplication, division).
- Support for array operations like reshaping, reversing, and sorting.
- Display results in a user-friendly format.

#### Implementation:
- Use the `APLArray` class for backend computations.
- For CLI: Use Python's `input()` and `print()` functions.
- For GUI: Use a library like [Tkinter](https://docs.python.org/3/library/tkinter.html)
   or [PyQt](https://www.riverbankcomputing.com/software/pyqt/).

#### Example CLI Interaction:
```
> Enter array: 1 2 3 4 5 6
> Enter operation: reshape 2 3
Result:
[[1 2 3]
 [4 5 6]]
```



### 3. Extend the `APLArray` Class with New Functionality
Add new features to the `APLArray` class to make it more powerful and versatile.

#### Ideas for New Features:
- Statistical Functions:
  - Add methods for mean, median, standard deviation, etc.
  - Example: `array.mean()`, `array.median()`.
- Advanced Indexing:
  - Add support for boolean indexing, fancy indexing, and slicing.
  - Example: `array[array > 5]`.
- File I/O:
  - Add methods for reading/writing arrays to/from CSV, JSON, or binary files.
  - Example: `array.to_csv('data.csv')`, `array.from_json('data.json')`.
- Plotting:
  - Integrate with libraries like [Matplotlib](https://matplotlib.org/) to visualize arrays.
  - Example: `array.plot()`.

#### Example Implementation:
```python
class APLArray:
    # Existing methods...

    def mean(self):
        return np.mean(self.data)

    def plot(self):
        import matplotlib.pyplot as plt
        plt.plot(self.data)
        plt.show()
```



### 4. Build a Data Analysis Toolkit

Create a toolkit for data analysis using the `APLArray` class. This toolkit can include functions
for cleaning, transforming, and analysing datasets.

#### Features:
- Data cleaning: Handle missing values, remove duplicates.
- Data transformation: Reshape, filter, and aggregate data.
- Data analysis: Compute summary statistics, correlations, and trends.

#### Example Workflow:
```python
# Load dataset
data = APLArray.from_csv('sales.csv')

# Clean data
data = data.drop_duplicates()
data = data.fill_missing(0)

# Analyze data
total_sales = data[:, 'Quantity'] * data[:, 'Price']
print("Total Sales:", total_sales.sum())
```



### 5. Create a Compiler for APL-like Expressions
Build a compiler that translates APL-like expressions into Python code or machine code.
This project will involve writing a lexer, parser, and code generator.

#### Steps:
1. Define the grammar for APL-like expressions.
2. Implement a lexer to tokenise the input.
3. Implement a parser to generate an abstract syntax tree (AST).
4. Generate Python code or machine code from the AST.

#### Example Input:
```apl
A ← 1 2 3 4 5
B ← A + 10
C ← B ⍴ 2 3
```

#### Example Output:
```python
A = APLArray([1, 2, 3, 4, 5])
B = A + 10
C = B.reshape(2, 3)
```

#### Tools:
- Use a parsing library like [Lark](https://github.com/lark-parser/lark) or [ANTLR](https://www.antlr.org/).
- Generate Python code using the `ast` module.



### 6. Build a Machine Learning Library
Create a lightweight machine learning library that uses the `APLArray` class for numerical computations.
Focus on basic algorithms like linear regression, k-means clustering, and decision trees.

#### Features:
- Support for vectorized operations using `APLArray`.
- Implement algorithms like linear regression and k-means clustering.
- Provide a simple API for training and prediction.

#### Example Usage:
```python
# Load dataset
X = APLArray([[1, 2], [2, 3], [3, 4]])
y = APLArray([1, 2, 3])

# Train a linear regression model
model = LinearRegression()
model.fit(X, y)

# Make predictions
predictions = model.predict(X)
```



### 7. Create a Game Using Array Operations
Build a simple game that relies heavily on array operations. For example, you could create a
puzzle game where players manipulate arrays to solve challenges.

#### Game Ideas:
- Array Puzzle: Players reshape, rotate, and filter arrays to match a target configuration.
- Matrix Maze: Players navigate a maze represented as a 2D array, using array operations to move and solve puzzles.

#### Example Gameplay:
```
Puzzle:
[[1, 2, 3],
 [4, 5, 6]]

Goal:
[[3, 2, 1],
 [6, 5, 4]]

Player Command: reverse rows
Result:
[[3, 2, 1],
 [6, 5, 4]]
Puzzle Solved!
```



### 8. Build a Visualisation Tool for Array Operations
Create a tool that visualises array operations step-by-step. This can help users understand
how operations like reshaping, reversing, and sorting work.

#### Features:
- Visualise the input array and the result of each operation.
- Support for common operations like reshape, reverse, sort, and reduce.
- Interactive interface for users to experiment with array operations.

#### Implementation:
- Use a GUI library like [Tkinter](https://docs.python.org/3/library/tkinter.html)
  or [PyQt](https://www.riverbankcomputing.com/software/pyqt/).
- Use [Matplotlib](https://matplotlib.org/) for visualising arrays.



### Conclusion
These projects range from building a full-fledged DSL to creating practical applications
like data analysis toolkits and games. Each project will deepen your understanding of
array-oriented programming and give you hands-on experience with language design, parsing,
and computational tools.
