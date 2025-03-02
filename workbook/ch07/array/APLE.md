
## APL Extended: Array Programming Language Extension

APL (A Programming Language) is a high-level, concise, and expressive programming language designed
for array processing. It is known for its use of unique symbols (e.g., `⍴`, `⌽`, `⍋`) to represent
operations, making it highly compact and powerful for mathematical and data manipulation tasks. APL
operates on arrays as its fundamental data structure, enabling vectorised operations that are both
efficient and elegant.

* https://youtu.be/8kUQWuK1L4w The Origins of APL - 1974

* https://youtu.be/_DTpQ4Kk2wA APL Demonstration 1975


The `APLArray` class is inspired by APL's array-oriented paradigm, bringing its functionality to
Python using NumPy for efficient array operations. So the reading should go like:
*Array Programming Language Extension*.


### Group Summaries

#### Initialisation and Representation
- Purpose: Initialise the `APLArray` object and provide a readable representation of the array.
- Key Methods:
  - `__init__`: Converts input data (lists, scalars, or arrays) into a NumPy array.
  - `__repr__`: Returns a string representation of the array for debugging.
- Summary: This group handles the creation and display of `APLArray` objects, ensuring compatibility
  with various input types.


#### Array Manipulation
- Purpose: Reshape, flatten, transpose, or extract parts of the array.
- Key Methods:
  - `reshape`: Reshapes the array to a specified shape.
  - `flatten`: Converts the array into a 1D array.
  - `transpose`: Swaps the axes of a 2D array.
  - `diagonal`: Extracts the diagonal elements of a 2D array.
- Summary: These methods allow for flexible manipulation of array shapes and structures, similar
  to APL's powerful reshaping capabilities.



#### Indexing and Slicing
- Purpose: Access and manipulate elements of the array using 1-based indexing.
- Key Methods:
  - `__getitem__`: Implements 1-based indexing (APL-style).
  - `take`: Extracts the first `n` elements (or last `n` if negative).
  - `drop`: Removes the first `n` elements (or last `n` if negative).
- Summary: This group provides APL-style indexing and slicing, making it easier to work with arrays
  in a way that aligns with APL's conventions.



#### Arithmetic
- Purpose: Perform element-wise arithmetic operations on arrays.
- Key Methods:
  - `__add__`, `__sub__`, `__mul__`, `__truediv__`: Implement addition, subtraction,
    multiplication, and ("true") division.
- Summary: These methods enable vectorized arithmetic operations, a core feature of APL's
  array-oriented programming.



#### Outer Operations
- Purpose: Compute outer products and sums, inspired by APL's `∘.` (outer product) operator.
- Key Methods:
  - `outer_sum`: Computes the outer sum of two arrays.
  - `outer_product`: Computes the outer product of two arrays.
- Summary: These methods replicate APL's ability to perform outer operations, which are useful
  for matrix and tensor computations.



#### APL-Style Functions
- Purpose: Implement common APL operations like reversing, rotating, and finding unique elements.
- Key Methods:
  - `reverse`: Reverses the array.
  - `rotate`: Rotates the array by a specified number of positions.
  - `unique`: Returns unique elements in the array.
  - `grade_up`, `grade_down`: Return indices for sorting in ascending or descending order.
- Summary: This group encapsulates APL's iconic functions, providing a Pythonic way to perform array
  transformations.



#### Reduction and Scanning
- Purpose: Perform reduction (e.g., sum, product) and cumulative operations (e.g., cumulative sum).
- Key Methods:
  - `reduce`: Reduces the array using a binary operation.
  - `scan`: Performs a cumulative operation (e.g., cumulative sum).
- Summary: These methods replicate APL's reduction (`/`) and scan (`\`) operators, which are essential
  for array processing.



#### Set Operations
- Purpose: Perform set operations like union, intersection, and difference.
- Key Methods:
  - `membership`: Checks if elements of one array are in another.
  - `intersection`, `union`, `difference`: Perform set operations on arrays.
- Summary: This group provides APL-like set operations, enabling efficient manipulation of array elements.



#### Matrix Operations
- Purpose: Perform linear algebra operations like dot products, cross products, and determinants.
- Key Methods:
  - `dot`: Computes the dot product of two arrays.
  - `cross`: Computes the cross product of two 3D vectors.
  - `det`: Computes the determinant of a 2D array.
- Summary: These methods bring APL's matrix manipulation capabilities to Python, leveraging NumPy's
  linear algebra functions.



#### Decompositions
- Purpose: Perform matrix decompositions like eigenvalue, SVD, QR, LU, and Cholesky.
- Key Methods:
  - `eig`: Computes eigenvalues and eigenvectors.
  - `svd`: Computes the singular value decomposition.
  - `qr`: Computes the QR decomposition.
- Summary: This group provides advanced matrix decomposition techniques, inspired by APL's
  mathematical prowess.



#### Array Concatenation and Splitting
- Purpose: Combine or split arrays along specified axes.
- Key Methods:
  - `vstack`, `hstack`: Stack arrays vertically or horizontally.
  - `concatenate`: Concatenate arrays along a specified axis.
  - `split`: Split the array into subarrays.
- Summary: These methods enable flexible array manipulation, similar to APL's array concatenation
  and splitting capabilities.



#### Array Padding and Rolling
- Purpose: Pad arrays with values or roll elements along axes.
- Key Methods:
  - `pad`: Pads the array with specified values.
  - `roll`: Rolls array elements along a specified axis.
- Summary: These methods replicate APL's ability to manipulate array boundaries and shift elements.



#### Array Reshaping and Broadcasting
- Purpose: Reshape arrays to match other arrays or broadcast to new shapes.
- Key Methods:
  - `reshape_like`: Reshapes the array to match another array's shape.
  - `broadcast_to`: Broadcasts the array to a new shape.
- Summary: These methods provide APL-like flexibility in reshaping and broadcasting arrays.



#### Array Selection and Filtering
- Purpose: Select or filter elements based on conditions or indices.
- Key Methods:
  - `where`: Returns elements where a condition is true.
  - `choose`: Constructs an array by selecting elements from `choices`.
  - `select`: Selects elements based on conditions.
- Summary: These methods replicate APL's powerful selection and filtering capabilities.



#### Array Creation and I/O
- Purpose: Create arrays from functions, iterables, or files, and save arrays to files.
- Key Methods:
  - `fromfunction`: Creates an array by evaluating a function over coordinates.
  - `fromiter`: Creates an array from an iterable.
  - `savetxt`: Saves the array to a text file.
- Summary: These methods provide APL-like array creation and I/O functionality.



#### Miscellaneous
- Purpose: Perform miscellaneous operations like computing norms, clipping values, or taking absolute values.
- Key Methods:
  - `norm`: Computes the Euclidean norm.
  - `clip`: Clips array values to a specified range.
  - `abs`: Returns absolute values.
- Summary: This group provides utility functions for common array operations.



### Conclusion

The `APLArray` class brings power and elegance of APL's array-oriented programming to Python,
leveraging NumPy for efficient computation. Each group of methods corresponds to a core aspect
of APL's functionality, making it easier to perform complex array manipulations in a concise
and expressive way.
