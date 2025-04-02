from collections import deque

def min_cost_grid(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    dp = [[float('inf')] * cols for _ in range(rows)]
    directions = [(-1,0), (1,0), (0,-1), (0,1)]  # Up, Down, Left, Right
    
    q = deque([goal])
    dp[goal[0]][goal[1]] = 0  # goal cost is 0

    while q:
        x, y = q.popleft()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # check bounds and obstacles (marked as -1 in grid)
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != -1:
                new_cost = dp[x][y] + 1  # assume movement cost is 1
                if new_cost < dp[nx][ny]:
                    dp[nx][ny] = new_cost
                    q.append((nx, ny))

    return dp[start[0]][start[1]] if dp[start[0]][start[1]] != float('inf') else -1


grid = [
    [0, 0, 0, 0, 0],
    [0, -1, -1, 0, 0],  # -1 = obstacle
    [0, 0, 0, -1, 0],
    [0, -1, 0, 0, 0],
    [0, 0, 0, 0, 0]
]
start = (0, 0)
goal = (4, 4)
print("Minimum cost:", min_cost_grid(grid, start, goal))  # Output: 8
# This function calculates the minimum cost to reach from start to goal in a grid
# with obstacles using BFS and dynamic programming.
# The grid is represented as a 2D list where -1 indicates an obstacle.
# The function returns the minimum cost or -1 if the goal is unreachable.
# The BFS ensures that we explore the shortest paths first, and the DP table
# keeps track of the minimum cost to reach each cell.
# The function is efficient for grids with obstacles and can handle large grids
# with multiple paths.