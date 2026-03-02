def solve_sudoku(board):
    """
    Solve a Sudoku puzzle using backtracking.
    board is a 9x9 list of lists, with 0 representing empty cells.
    """
    # Find an empty cell
    empty_cell = find_empty(board)
    
    # If no empty cell is found, the puzzle is solved
    if not empty_cell:
        return True
    
    row, col = empty_cell
    
    # Try digits 1-9
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            # Place the number
            board[row][col] = num
            
            # Recursively try to solve the rest of the puzzle
            if solve_sudoku(board):
                return True
            
            # If placing num didn't lead to a solution, backtrack
            board[row][col] = 0
    
    # No solution found with current board state
    return False

def find_empty(board):
    """Find an empty cell in the board."""
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def is_valid(board, row, col, num):
    """Check if placing num at board[row][col] is valid."""
    # Check row
    for j in range(9):
        if board[row][j] == num:
            return False
    
    # Check column
    for i in range(9):
        if board[i][col] == num:
            return False
    
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    
    # If we get here, the placement is valid
    return True

# Example Sudoku puzzle
example_board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Make a copy to avoid modifying the original
import copy
board_to_solve = copy.deepcopy(example_board)

# Solve the Sudoku
if solve_sudoku(board_to_solve):
    print("Sudoku solved!")
    for row in board_to_solve:
        print(row)
else:
    print("No solution exists.")