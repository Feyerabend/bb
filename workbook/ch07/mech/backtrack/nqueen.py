def solve_n_queens(n):
    """
    Solve the N-Queens problem using backtracking.
    Returns a list of solutions, where each solution is a list of column positions for each row.
    """
    def is_safe(board, row, col):
        # Check if a queen can be placed at board[row][col]
        
        # Check the column (no need to check row as we place one queen per row)
        for i in range(row):
            if board[i] == col:
                return False
        
        # Check upper-left diagonal
        for i, j in zip(range(row-1, -1, -1), range(col-1, -1, -1)):
            if board[i] == j:
                return False
        
        # Check upper-right diagonal
        for i, j in zip(range(row-1, -1, -1), range(col+1, n)):
            if board[i] == j:
                return False
        
        return True
    
    def backtrack(row, current_solution, solutions):
        if row == n:
            # Found a valid solution
            solutions.append(current_solution[:])
            return
        
        for col in range(n):
            if is_safe(current_solution, row, col):
                # Place queen
                current_solution[row] = col
                
                # Recur to place rest of the queens
                backtrack(row + 1, current_solution, solutions)
                
                # Backtrack: remove queen to try other positions
                # (This line is conceptual, as we overwrite the value in the next iteration)
    
    solutions = []
    # Initialize board: -1 means no queen is placed yet
    board = [-1] * n
    backtrack(0, board, solutions)
    return solutions

# Test with 4-Queens
solutions = solve_n_queens(4)
print(f"Found {len(solutions)} solutions:")

# Print the solutions in a more readable format
for i, solution in enumerate(solutions):
    print(f"Solution {i+1}:")
    for row in range(len(solution)):
        line = ['.'] * len(solution)
        line[solution[row]] = 'Q'
        print(' '.join(line))
    print()