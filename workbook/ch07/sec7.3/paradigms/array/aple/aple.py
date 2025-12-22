
import numpy as np
import scipy.linalg

class APLArray:

    def __init__(self, data):
        """Initialize with a NumPy array for easy vectorized operations."""
        if isinstance(data, list):
            self.data = np.array(data)
        elif isinstance(data, (int, float)):  # allow for scalars
            self.data = np.array([data])
        else:
            self.data = np.array(data)

    def __repr__(self):
        return f"APLArray({self.data.tolist()})"

    def reshape(self, *shape):
        """⍴ - Reshape the array to the given shape."""
        # total number of elements in the new shape
        total_elements = np.prod([s for s in shape if s != -1])
        if -1 in shape:
            # if -1 is present, calculate the size of the -1 dimension
            inferred_size = self.data.size // total_elements
            shape = [inferred_size if s == -1 else s for s in shape]
        if np.prod(shape) != self.data.size:
            raise ValueError(f"Cannot reshape array of size {self.data.size} into shape {shape} (total elements mismatch)")
        return APLArray(self.data.reshape(shape))

    def broadcast_match(self, other):
        """Resize both arrays to match the longest size (APL-style broadcasting)."""
        max_len = max(len(self.data), len(other.data))
        return APLArray(np.resize(self.data, max_len)), APLArray(np.resize(other.data, max_len))


    def __getitem__(self, index):
        if isinstance(index, tuple):
            # Handle 2D slicing
            return APLArray(self.data[index])
        elif isinstance(index, int):
            # Handle 1D indexing
            if 1 <= index <= len(self.data):
                return self.data[index - 1]  # 1-based to 0-based Python
            raise IndexError("APL indexing out of bounds (1-based)")
        elif isinstance(index, list):
            return APLArray([self[i] for i in index])
        else:
            raise TypeError("Invalid index type")

#        elif isinstance(index, list):
#            return APLArray([self[i] for i in index])
#        return APLArray(self.data[index - 1])


    # arithmetic
    def __add__(self, other):
        if isinstance(other, APLArray):
            x, y = self.broadcast_match(other)
            return APLArray(x.data + y.data)
        return APLArray(self.data + other)

    def __sub__(self, other):
        if isinstance(other, APLArray):
            x, y = self.broadcast_match(other)
            return APLArray(x.data - y.data)
        return APLArray(self.data - other)


    def __mul__(self, other):
        if isinstance(other, APLArray):
            x, y = self.broadcast_match(other)
            return APLArray(x.data * y.data)
        return APLArray(self.data * other)

#    def __truediv__(self, other):
#        if isinstance(other, APLArray):
#            # Broadcast the smaller array to match the larger array
#            if len(self.data) > len(other.data):
#                other_data = np.resize(other.data, len(self.data))
#                return APLArray(self.data / other_data)
#            else:
#                self_data = np.resize(self.data, len(other.data))
#                return APLArray(self_data / other.data)
#        return APLArray(self.data / other)


    def __truediv__(self, other):
        if isinstance(other, APLArray):
            x, y = self.broadcast_match(other)
            return APLArray(x.data / y.data)
        return APLArray(self.data / other)

    def __floordiv__(self, other):
        if isinstance(other, APLArray):
            x, y = self.broadcast_match(other)
            return APLArray(x.data // y.data)
        return APLArray(self.data // other)

    # Outer Operations (APL ∘.× and ∘.+)
    def outer_sum(self, other):
        """Outer addition (APL's ∘.+)"""
        return APLArray(self.data[:, None] + other.data)

    def outer_product(self, other):
        """Outer multiplication (APL's ∘.*)"""
        return APLArray(self.data[:, None] * other.data)

    # APL Functions
    def reverse(self):
        """⌽ - Reverse the array."""
        return APLArray(self.data[::-1])

    def rotate(self, n):
        """⊖ - Rotate left by n positions."""
        return APLArray(np.roll(self.data, -n))

    def unique(self):
        """∪ - Return unique elements."""
        return APLArray(np.unique(self.data))

    def take(self, n):
        """↑ - Take the first n elements."""
        return APLArray(self.data[:n]) if n >= 0 else APLArray(self.data[n:])

    def drop(self, n):
        """↓ - Drop the first n elements."""
        return APLArray(self.data[n:]) if n >= 0 else APLArray(self.data[:n])

    def grade_up(self):
        """⍋ - Grade up: Return indices that would sort the array in ascending order."""
        return APLArray(np.argsort(self.data) + 1)  # Convert to 1-based index

    def grade_down(self):
        """⍒ - Grade down: Return indices for descending order."""
        return APLArray(np.argsort(-self.data) + 1)

    def reduce(self, op):
        """Reduce the array using a binary operation (e.g., sum, product)."""
        if op == '+':
            return APLArray(np.sum(self.data))
        elif op == '*':
            return APLArray(np.prod(self.data))
        elif op == 'max':
            return APLArray(np.max(self.data))
        elif op == 'min':
            return APLArray(np.min(self.data))
        else:
            raise ValueError(f"Unsupported operation: {op}")

    def scan(self, op):
        """Scan the array using a binary operation (e.g., cumulative sum, product)."""
        if op == '+':
            return APLArray(np.cumsum(self.data))
        elif op == '*':
            return APLArray(np.cumprod(self.data))
        else:
            raise ValueError(f"Unsupported operation: {op}")

    def compress(self, mask):
        """Compress the array using a boolean mask."""
        if len(mask) != len(self.data):
            raise ValueError("Mask length must match array length")
        return APLArray(self.data[mask])

    def expand(self, mask, fill_value=0):
        """Expand the array using a boolean mask, filling with a value."""
        result = np.full(len(mask), fill_value)
        result[mask] = self.data
        return APLArray(result)

    def where(self, condition):
        """Return indices where the condition is true."""
        return APLArray(np.where(condition(self.data))[0] + 1)  # 1-based indexing

    def replicate(self, counts):
        """Replicate elements based on counts."""
        return APLArray(np.repeat(self.data, counts))

    def membership(self, other):
        """Check membership of elements in another array."""
        return APLArray(np.isin(self.data, other.data))

    def intersection(self, other):
        """Return the intersection of two arrays."""
        return APLArray(np.intersect1d(self.data, other.data))

    def union(self, other):
        """Return the union of two arrays."""
        return APLArray(np.union1d(self.data, other.data))

    def difference(self, other):
        """Return the difference of two arrays."""
        return APLArray(np.setdiff1d(self.data, other.data))

    def symmetric_difference(self, other):
        """Return the symmetric difference of two arrays."""
        return APLArray(np.setxor1d(self.data, other.data))

    def reshape_auto(self):
        """Automatically reshape the array into a square matrix if possible."""
        size = len(self.data)
        sqrt_size = int(np.sqrt(size))
        if sqrt_size * sqrt_size == size:
            return self.reshape(sqrt_size, sqrt_size)
        raise ValueError("Cannot reshape into a square matrix")

    def resize(self, shape):
        """Resize the array to the specified shape."""
        return APLArray(np.resize(self.data, shape))

    def transpose(self):
        """Transpose the array (for 2D arrays)."""
        return APLArray(self.data.T)

    def diagonal(self):
        """Extract the diagonal of a 2D array."""
        return APLArray(np.diag(self.data))

    def flatten(self):
        """Flatten the array into a 1D array."""
        return APLArray(self.data.flatten())

    def sort(self):
        """Sort the array in ascending order."""
        return APLArray(np.sort(self.data))

    def argsort(self):
        """Return the indices that would sort the array."""
        return APLArray(np.argsort(self.data) + 1)  # 1-based indexing

    def rank(self):
        """Return the rank of the array (number of dimensions)."""
        return len(self.data.shape)

    @property
    def shape(self):
        """Return the shape of the array."""
        return self.data.shape

    def size(self):
        """Return the total number of elements in the array."""
        return self.data.size

    def any(self):
        """Return True if any element is non-zero."""
        return np.any(self.data)

    def all(self):
        """Return True if all elements are non-zero."""
        return np.all(self.data)

    def sum(self, axis=None):
        """Return the sum of all elements along the specified axis."""
        return APLArray(np.sum(self.data, axis=axis))

    def mean(self):
        """Return the mean of all elements."""
        return np.mean(self.data)

    def std(self):
        """Return the standard deviation of all elements."""
        return np.std(self.data)

    def min(self):
        """Return the minimum value in the array."""
        return np.min(self.data)

    def max(self):
        """Return the maximum value in the array."""
        return np.max(self.data)

    def argmin(self):
        """Return the index of the minimum value (1-based)."""
        return np.argmin(self.data) + 1

    def argmax(self):
        """Return the index of the maximum value (1-based)."""
        return np.argmax(self.data) + 1

    def clip(self, min_val, max_val):
        """Clip the array values to the specified range."""
        return APLArray(np.clip(self.data, min_val, max_val))

    def abs(self):
        """Return the absolute values of the array."""
        return APLArray(np.abs(self.data))

    def log(self):
        """Return the natural logarithm of the array."""
        return APLArray(np.log(self.data))

    def exp(self):
        """Return the exponential of the array."""
        return APLArray(np.exp(self.data))

    def sqrt(self):
        """Return the square root of the array."""
        return APLArray(np.sqrt(self.data))

    def power(self, exponent):
        """Raise the array elements to the specified power."""
        return APLArray(np.power(self.data, exponent))

    def dot(self, other):
        """Compute the dot product with another array."""
        return APLArray(np.dot(self.data, other.data))

    def cross(self, other):
        """Compute the cross product with another array (for 3D vectors)."""
        return APLArray(np.cross(self.data, other.data))

    def norm(self):
        """Compute the Euclidean norm of the array."""
        return np.linalg.norm(self.data)

    def det(self):
        """Compute the determinant of a 2D array."""
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("Determinant is only defined for square matrices.")
        return np.linalg.det(self.data)

    def inv(self):
        """Compute the inverse of a 2D array."""
        return APLArray(np.linalg.inv(self.data))

    def eig(self):
        """Compute the eigenvalues and eigenvectors of a 2D array."""
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("Eigenvalue decomposition is only defined for square matrices.")
        eigenvalues, eigenvectors = np.linalg.eig(self.data)
        return APLArray(eigenvalues), APLArray(eigenvectors)

    def svd(self):
        """Compute the singular value decomposition of a 2D array."""
        U, S, V = np.linalg.svd(self.data)
        return APLArray(U), APLArray(S), APLArray(V)

    def qr(self):
        """Compute the QR decomposition of a 2D array."""
        Q, R = np.linalg.qr(self.data)
        return APLArray(Q), APLArray(R)

    def lu(self):
        """Compute the LU decomposition of a 2D array."""
        P, L, U = scipy.linalg.lu(self.data)
        return APLArray(P), APLArray(L), APLArray(U)

    def cholesky(self):
        """Compute the Cholesky decomposition of a 2D array."""
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("Cholesky decomposition is only defined for square matrices.")
        if not np.allclose(self.data, self.data.T):
            raise ValueError("Matrix must be symmetric for Cholesky decomposition.")
        try:
            return APLArray(np.linalg.cholesky(self.data))
        except np.linalg.LinAlgError:
            raise ValueError("Matrix is not positive definite.")

    def solve(self, b):
        """Solve the linear system Ax = b."""
        return APLArray(np.linalg.solve(self.data, b.data))

    def lstsq(self, b):
        """Solve the least squares problem Ax = b."""
        return APLArray(np.linalg.lstsq(self.data, b.data, rcond=None)[0])

    def pinv(self):
        """Compute the pseudo-inverse of a 2D array."""
        return APLArray(np.linalg.pinv(self.data))

    def rank_matrix(self):
        """Compute the rank of a 2D array."""
        return np.linalg.matrix_rank(self.data)

    def trace(self):
        """Compute the trace of a 2D array."""
        return np.trace(self.data)

    def diag(self):
        """Extract the diagonal of a 2D array."""
        return APLArray(np.diag(self.data))

    def triu(self):
        """Extract the upper triangular part of a 2D array."""
        return APLArray(np.triu(self.data))

    def tril(self):
        """Extract the lower triangular part of a 2D array."""
        return APLArray(np.tril(self.data))

    def vstack(self, other):
        """Stack arrays vertically."""
        # reshape 1D arrays to 2D arrays with one column
        self_data = self.data.reshape(-1, 1) if self.data.ndim == 1 else self.data
        other_data = other.data.reshape(-1, 1) if other.data.ndim == 1 else other.data
        return APLArray(np.vstack((self_data, other_data)))

    def hstack(self, other):
        """Stack arrays horizontally."""
        return APLArray(np.hstack((self.data, other.data)))

    def concatenate(self, other, axis=0):
        """Concatenate arrays along the specified axis."""
        return APLArray(np.concatenate((self.data, other.data), axis=axis))

    def split(self, indices, axis=0):
        """Split the array into subarrays along the specified axis."""
        return [APLArray(arr) for arr in np.split(self.data, indices, axis=axis)]

    def tile(self, reps):
        """Repeat the array a specified number of times."""
        return APLArray(np.tile(self.data, reps))

    def repeat(self, repeats, axis=None):
        """Repeat elements of the array."""
        return APLArray(np.repeat(self.data, repeats, axis=axis))

    def pad(self, pad_width, mode='constant', constant_values=0):
        """Pad the array with specified values."""
        return APLArray(np.pad(self.data, pad_width, mode=mode, constant_values=constant_values))

    def roll(self, shift, axis=None):
        """Roll the array elements along the specified axis."""
        return APLArray(np.roll(self.data, -shift, axis=axis))  # -shift for left roll

    def flip(self, axis=None):
        """Reverse the order of elements along the specified axis."""
        return APLArray(np.flip(self.data, axis=axis))

    def rot90(self, k=1, axes=(0, 1)):
        """Rotate the array by 90 degrees in the plane specified by axes."""
        if self.data.ndim != 2:
            raise ValueError("Rotation is only supported for 2D arrays.")
        if axes[0] == axes[1]:
            raise ValueError("Axes must be different.")
        return APLArray(np.rot90(self.data, k=k, axes=axes))

    def squeeze(self):
        """Remove single-dimensional entries from the shape of the array."""
        squeezed_data = np.squeeze(self.data)
        if squeezed_data.ndim == 0:
            return APLArray([squeezed_data.item()])
        return APLArray(squeezed_data.ravel())

    def expand_dims(self, axis):
        """Expand the shape of the array by inserting a new axis."""
        return APLArray(np.expand_dims(self.data, axis=axis))

    def swapaxes(self, axis1, axis2):
        """Swap two axes of the array."""
        return APLArray(np.swapaxes(self.data, axis1, axis2))

    def moveaxis(self, source, destination):
        """Move axes of the array to new positions."""
        return APLArray(np.moveaxis(self.data, source, destination))

    def broadcast_to(self, shape):
        """Broadcast the array to a new shape."""
        return APLArray(np.broadcast_to(self.data, shape))

    def ravel(self):
        """Return a flattened array."""
        return APLArray(np.ravel(self.data))

    def reshape_like(self, other):
        """Reshape the array to match the shape of another array, padding or truncating if necessary."""
        target_size = np.prod(other.shape)
        if self.data.size < target_size:
            # pad with zeros if x is smaller than target size
            padded_data = np.pad(self.data, (0, target_size - self.data.size), mode='constant')
            return APLArray(padded_data.reshape(other.shape))
        elif self.data.size > target_size:
            # truncate if x is larger than target size
            truncated_data = self.data[:target_size]
            return APLArray(truncated_data.reshape(other.shape))
        else:
            # reshape directly if sizes match
            return APLArray(self.data.reshape(other.shape))

    def where(self, condition):
        """Return elements where the condition is true."""
        return APLArray(self.data[condition(self.data)])

    def choose(self, choices):
        """Construct an array by choosing elements from choices, using 1-based indices."""
        choices = np.array(choices)
        if self.data.dtype.kind not in 'iu':  # check if data integer type
            raise ValueError("Indices must be integers")
        indices = self.data  # 1-based indices
        wrapped_indices = (indices - 1) % len(choices)  # to 0-based and wrap
        selected = choices[wrapped_indices]
        return APLArray(selected)

    def select(self, condlist, choicelist, default=0):
        """Select elements from choicelist based on condlist, with a default value for False conditions."""
        return APLArray(np.select(condlist, choicelist, default=default))

    def piecewise(self, condlist, funclist):
        """Evaluate a piecewise-defined function."""
        return APLArray(np.piecewise(self.data, condlist, funclist))

    def apply_along_axis(self, func, axis):
        """Apply a function along the specified axis."""
        return APLArray(np.apply_along_axis(func, axis, self.data))

    def apply_over_axes(self, func, axes):
        """Apply a function over multiple axes."""
        # flatten array and apply the function if all axes specified
        if set(axes) == set(range(self.data.ndim)):
            result = func(self.data.flatten())
        else:
            result = np.apply_over_axes(func, self.data, axes)
        return APLArray(result)

    def vectorize(self, func):
        """Vectorize a function to operate on the array."""
        return APLArray(np.vectorize(func)(self.data))

    @classmethod
    def fromfunction(cls, func, shape):
        """Construct an array by executing a function over each coordinate."""
        return cls(np.fromfunction(func, shape))

    @classmethod
    def fromiter(cls, iterable, dtype):
        """Create an array from an iterable."""
        return cls(np.fromiter(iterable, dtype))

    @classmethod
    def fromstring(cls, string, dtype, sep=' '):
        """Create an array from a string with a specified separator."""
        return cls(np.fromstring(string, dtype=dtype, sep=sep))

    def fromfile(self, file, dtype, count=-1, sep=''):
        """Create an array from a file."""
        return APLArray(np.fromfile(file, dtype, count, sep))

    def frombuffer(self, buffer, dtype, count=-1, offset=0):
        """Create an array from a buffer."""
        return APLArray(np.frombuffer(buffer, dtype, count, offset))

    def fromregex(self, file, regexp, dtype):
        """Create an array from a text file using a regular expression."""
        return APLArray(np.fromregex(file, regexp, dtype))

    def fromrecords(self, records, dtype=None):
        """Create an array from a list of records."""
        return APLArray(np.fromrecords(records, dtype))

    @classmethod
    def fromtxt(cls, file, dtype=float, comments='#', delimiter=None, converters=None, skiprows=0, usecols=None, unpack=False, ndmin=0):
        """Load data from a text file."""
        data = np.loadtxt(file, dtype=float, comments=comments, delimiter=delimiter, converters=converters, skiprows=skiprows, usecols=usecols, unpack=unpack, ndmin=ndmin)
        if dtype == int:
            data = data.astype(np.int64)
        return cls(data)
    
    def genfromtxt(self, file, dtype=float, comments='#', delimiter=None, skip_header=0, skip_footer=0, converters=None, missing_values=None, filling_values=None, usecols=None, names=None, excludelist=None, deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', unpack=False, usemask=False, loose=True, invalid_raise=True, max_rows=None):
        """Load data from a text file with missing values handled."""
        return APLArray(np.genfromtxt(file, dtype, comments, delimiter, skip_header, skip_footer, converters, missing_values, filling_values, usecols, names, excludelist, deletechars, replace_space, autostrip, case_sensitive, defaultfmt, unpack, usemask, loose, invalid_raise, max_rows))

    def savetxt(self, file, fmt='%.18e', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None):
        """Save the array to a text file."""
        np.savetxt(file, self.data, fmt, delimiter, newline, header, footer, comments, encoding)

    def tofile(self, file, sep='', format='%s'):
        """Write the array to a file as text or binary."""
        self.data.tofile(file, sep, format)

    def dump(self, file):
        """Dump the array to a file in binary format."""
        self.data.dump(file)

    def dumps(self):
        """Return the array as a binary string."""
        return self.data.dumps()

    @classmethod
    def load(cls, file):
        """Load an array from a binary file."""
        return cls(np.load(file))

    def loads(self, str):
        """Load an array from a binary string."""
        return APLArray(np.loads(str))

    def save(self, file):
        """Save the array to a binary file."""
        np.save(file, self.data)

    def savez(self, file, *args, **kwargs):
        """Save several arrays into a single file in uncompressed .npz format."""
        np.savez(file, *args, **kwargs)

    def savez_compressed(self, file, *args, **kwargs):
        """Save several arrays into a single file in compressed .npz format."""
        np.savez_compressed(file, *args, **kwargs)

    def loadtxt(self, file, dtype=float, comments='#', delimiter=None, converters=None, skiprows=0, usecols=None, unpack=False, ndmin=0):
        """Load data from a text file."""
        return APLArray(np.loadtxt(file, dtype, comments, delimiter, converters, skiprows, usecols, unpack, ndmin))

