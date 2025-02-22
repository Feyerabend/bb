
import numpy as np
import scipy.linalg
from aple import APLArray

# Create some sample arrays
x = APLArray([3, 1, 4, 1, 5, 9])
y = APLArray([10, 20, 30])
z = APLArray([[1, 2, 3], [4, 5, 6]])

# Test 1: Arithmetic Operations
assert (x + y).data.tolist() == [13, 21, 34, 11, 25, 39], "Addition failed"
assert (x - y).data.tolist() == [-7, -19, -26, -9, -15, -21], "Subtraction failed"
assert (x * y).data.tolist() == [30, 20, 120, 10, 100, 270], "Multiplication failed"
assert (x / y).data.tolist() == [0.3, 0.05, 0.13333333333333333, 0.1, 0.25, 0.3], "Division failed"
#assert (x / y).data.tolist() == [0.3, 0.05, 0.13333333333333333, 0.1, 0.2, 0.3], "Division failed"

# Test 2: Indexing (1-based)
assert x[1] == 3, "Indexing failed"
assert x[3] == 4, "Indexing failed"
assert x[[1, 3, 5]].data.tolist() == [3, 4, 5], "Indexing with list failed"

# Test 3: Reshape
assert x.reshape(2, 3).data.tolist() == [[3, 1, 4], [1, 5, 9]], "Reshape failed"
assert y.reshape(3, 1).data.tolist() == [[10], [20], [30]], "Reshape failed"

# Test 4: Take and Drop
assert x.take(4).data.tolist() == [3, 1, 4, 1], "Take failed"
assert x.drop(2).data.tolist() == [4, 1, 5, 9], "Drop failed"

# Test 5: Grade Up and Grade Down
assert x.grade_up().data.tolist() == [2, 4, 1, 3, 5, 6], "Grade Up failed"
assert x.grade_down().data.tolist() == [6, 5, 3, 1, 2, 4], "Grade Down failed"

# Test 6: Outer Operations
assert x.outer_sum(y).data.tolist() == [
    [13, 23, 33],
    [11, 21, 31],
    [14, 24, 34],
    [11, 21, 31],
    [15, 25, 35],
    [19, 29, 39]
], "Outer Sum failed"
assert x.outer_product(y).data.tolist() == [
    [30, 60, 90],
    [10, 20, 30],
    [40, 80, 120],
    [10, 20, 30],
    [50, 100, 150],
    [90, 180, 270]
], "Outer Product failed"

# Test 7: Reverse and Rotate
assert x.reverse().data.tolist() == [9, 5, 1, 4, 1, 3], "Reverse failed"
assert x.rotate(2).data.tolist() == [4, 1, 5, 9, 3, 1], "Rotate failed"

# Test 8: Unique
assert APLArray([1, 2, 2, 3, 3, 3, 4]).unique().data.tolist() == [1, 2, 3, 4], "Unique failed"

# Test 9: Reduce and Scan
assert x.reduce('+').data.tolist() == 23, "Reduce (sum) failed"
assert x.reduce('*').data.tolist() == 540, "Reduce (product) failed"
assert x.scan('+').data.tolist() == [3, 4, 8, 9, 14, 23], "Scan (cumulative sum) failed"

# Test 10: Membership and Set Operations
assert x.membership(y).data.tolist() == [False, False, False, False, False, False], "Membership failed"
assert x.intersection(APLArray([1, 3, 5])).data.tolist() == [1, 3, 5], "Intersection failed"
assert x.union(APLArray([1, 2, 3])).data.tolist() == [1, 2, 3, 4, 5, 9], "Union failed"
assert x.difference(APLArray([1, 3, 5])).data.tolist() == [4, 9], "Difference failed"

# Test 11: Matrix Operations
assert z.transpose().data.tolist() == [[1, 4], [2, 5], [3, 6]], "Transpose failed"
assert z.diagonal().data.tolist() == [1, 5], "Diagonal failed"

# Test 12: Flatten and Sort
assert z.flatten().data.tolist() == [1, 2, 3, 4, 5, 6], "Flatten failed"
assert x.sort().data.tolist() == [1, 1, 3, 4, 5, 9], "Sort failed"

# Test 13: Clip and Abs
assert x.clip(2, 5).data.tolist() == [3, 2, 4, 2, 5, 5], "Clip failed"
assert APLArray([-1, -2, 3]).abs().data.tolist() == [1, 2, 3], "Abs failed"

# Test 14: Log and Exp
assert np.allclose(x.log().data, np.log([3, 1, 4, 1, 5, 9])), "Log failed"
assert np.allclose(x.exp().data, np.exp([3, 1, 4, 1, 5, 9])), "Exp failed"

# Test 15: Dot Product and Cross Product
a = APLArray([1, 2, 3])
b = APLArray([4, 5, 6])
assert a.dot(b).data.tolist() == 32, "Dot product failed"
assert a.cross(b).data.tolist() == [-3, 6, -3], "Cross product failed"

# Test 16: Norm and Determinant
assert np.isclose(a.norm(), np.linalg.norm([1, 2, 3])), "Norm failed"

# Use a square matrix for determinant test
square_matrix = APLArray([[1, 2], [3, 4]])
assert np.isclose(square_matrix.det(), -2.0), "Determinant failed"

# Test 17: Eigenvalues and Eigenvectors
eigenvalues, eigenvectors = square_matrix.eig()
assert np.allclose(eigenvalues.data, np.linalg.eig([[1, 2], [3, 4]])[0]), "Eigenvalues failed"
assert np.allclose(eigenvectors.data, np.linalg.eig([[1, 2], [3, 4]])[1]), "Eigenvectors failed"

# Test 18: SVD
U, S, V = square_matrix.svd()
assert np.allclose(U.data, np.linalg.svd([[1, 2], [3, 4]])[0]), "SVD (U) failed"
assert np.allclose(S.data, np.linalg.svd([[1, 2], [3, 4]])[1]), "SVD (S) failed"
assert np.allclose(V.data, np.linalg.svd([[1, 2], [3, 4]])[2]), "SVD (V) failed"

# Test 19: QR Decomposition
Q, R = square_matrix.qr()
assert np.allclose(Q.data, np.linalg.qr([[1, 2], [3, 4]])[0]), "QR (Q) failed"
assert np.allclose(R.data, np.linalg.qr([[1, 2], [3, 4]])[1]), "QR (R) failed"

# Test 20: LU Decomposition
P, L, U = square_matrix.lu()
P_ref, L_ref, U_ref = scipy.linalg.lu([[1, 2], [3, 4]])
assert np.allclose(P.data, P_ref), "LU (P) failed"
assert np.allclose(L.data, L_ref), "LU (L) failed"
assert np.allclose(U.data, U_ref), "LU (U) failed"

# Test 21: Cholesky Decomposition
positive_definite_matrix = APLArray([[4, 1], [1, 4]])
assert np.allclose(positive_definite_matrix.cholesky().data, np.linalg.cholesky([[4, 1], [1, 4]])), "Cholesky failed"

# Test 22: Solve Linear System
A = APLArray([[3, 2], [1, 4]])
b = APLArray([5, 6])
assert np.allclose(A.solve(b).data, np.linalg.solve([[3, 2], [1, 4]], [5, 6])), "Solve failed"

# Test 23: Least Squares
assert np.allclose(A.lstsq(b).data, np.linalg.lstsq([[3, 2], [1, 4]], [5, 6], rcond=None)[0]), "Least Squares failed"

# Test 24: Pseudo-Inverse
assert np.allclose(square_matrix.pinv().data, np.linalg.pinv([[1, 2], [3, 4]])), "Pseudo-Inverse failed"

# Test 25: Rank and Trace
assert square_matrix.rank_matrix() == np.linalg.matrix_rank([[1, 2], [3, 4]]), "Rank failed"
assert square_matrix.trace() == np.trace([[1, 2], [3, 4]]), "Trace failed"

# Test 26: Triangular Matrices
assert np.allclose(square_matrix.triu().data, np.triu([[1, 2], [3, 4]])), "Upper triangular failed"
assert np.allclose(square_matrix.tril().data, np.tril([[1, 2], [3, 4]])), "Lower triangular failed"

# Test 27: Stacking and Concatenation
x_reshaped = x.reshape(-1, 1)
y_reshaped = y.reshape(-1, 1)
assert np.allclose(x_reshaped.vstack(y_reshaped).data, np.vstack((x_reshaped.data, y_reshaped.data))), "Vertical stack failed"
assert np.allclose(x.hstack(y).data, np.hstack((x.data, y.data))), "Horizontal stack failed"
assert np.allclose(x.concatenate(y, axis=0).data, np.concatenate((x.data, y.data), axis=0)), "Concatenate failed"

# Test 28: Splitting
assert [arr.data.tolist() for arr in x.split([3])] == [[3, 1, 4], [1, 5, 9]], "Split failed"

# Test 29: Tile and Repeat
assert x.tile(2).data.tolist() == [3, 1, 4, 1, 5, 9, 3, 1, 4, 1, 5, 9], "Tile failed"
assert x.repeat(2).data.tolist() == [3, 3, 1, 1, 4, 4, 1, 1, 5, 5, 9, 9], "Repeat failed"

# Test 30: Pad and Roll
assert x.pad((2, 2)).data.tolist() == [0, 0, 3, 1, 4, 1, 5, 9, 0, 0], "Pad failed"
assert x.roll(2).data.tolist() == [4, 1, 5, 9, 3, 1], "Roll failed"

# Test 31: Flip and Rotate
assert x.flip().data.tolist() == [9, 5, 1, 4, 1, 3], "Flip failed"
z_rotated = z.rot90()
assert z_rotated.data.tolist() == [[3, 6], [2, 5], [1, 4]], "Rotate failed"

# Test 32: Squeeze and Expand
assert z.squeeze().data.tolist() == [1, 2, 3, 4, 5, 6], "Squeeze failed"
assert x.expand_dims(0).data.tolist() == [[3, 1, 4, 1, 5, 9]], "Expand dimensions failed"

# Test 33: Swap and Move Axes
assert z.swapaxes(0, 1).data.tolist() == [[1, 4], [2, 5], [3, 6]], "Swap axes failed"
assert z.moveaxis(0, 1).data.tolist() == [[1, 4], [2, 5], [3, 6]], "Move axes failed"

# Test 34: Broadcast
assert x.broadcast_to((2, 6)).data.tolist() == [
    [3, 1, 4, 1, 5, 9],
    [3, 1, 4, 1, 5, 9]
], "Broadcast failed"

# Test 35: Ravel and Reshape Like
assert z.ravel().data.tolist() == [1, 2, 3, 4, 5, 6], "Ravel failed"
assert x.reshape_like(y).data.tolist() == [3, 1, 4], "Reshape like failed"

# Test 36: Where and Choose
assert x.where(lambda a: a > 3).data.tolist() == [4, 5, 9], "Where failed"

#assert x.choose([10, 20, 30]).data.tolist() == [10, 20, 30, 10, 20, 30], "Choose failed"

x = APLArray([3, 1, 4, 1, 5, 9])
choices = [10, 20, 30]
expected_output = [30, 10, 10, 10, 20, 30]
result = x.choose(choices)   
assert result.data.tolist() == expected_output, f"Expected {expected_output}, but got {result.data.tolist()}"
 

# Test 37: Select and Piecewise
x = APLArray([1, 2, 3, 4, 5, 6])
assert x.select([x.data > 3], [10], default=0).data.tolist() == [0, 0, 0, 10, 10, 10], "Select failed"
assert x.piecewise([x.data > 3], [lambda a: a * 2, lambda a: a * 3]).data.tolist() == [3, 6, 9, 8, 10, 12], "Piecewise failed"

# Test 38: Apply Along Axis and Over Axes
assert z.apply_along_axis(np.sum, 0).data.tolist() == [5, 7, 9], "Apply along axis failed"
assert z.apply_over_axes(np.sum, [0, 1]).data.tolist() == 21, "Apply over axes failed"

# Test 39: Vectorize
assert x.vectorize(lambda a: a ** 2).data.tolist() == [1, 4, 9, 16, 25, 36], "Vectorize failed"

# Test 40: From Function and Iter
assert APLArray.fromfunction(lambda i, j: i + j, (3, 3)).data.tolist() == [
    [0.0, 1.0, 2.0],
    [1.0, 2.0, 3.0],
    [2.0, 3.0, 4.0]
], "From function failed"
assert APLArray.fromiter(range(5), int).data.tolist() == [0, 1, 2, 3, 4], "From iterable failed"

# Test 41: From String and File
result = APLArray.fromstring("1,2,3,4", int, sep=',')
assert result.data.tolist() == [1, 2, 3, 4], "From string failed"

# Test 42: Save and Load
x = APLArray([1, 2, 3, 4, 5, 6])
x.save("x.npy")
loaded_x = APLArray.load("x.npy")
assert loaded_x.data.tolist() == [1, 2, 3, 4, 5, 6], "Save and load failed"

print("All tests passed!")