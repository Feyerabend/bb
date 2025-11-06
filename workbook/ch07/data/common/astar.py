class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start
        self.h = 0  # Heuristic cost to goal
        self.f = 0  # Total cost

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid, start, goal):
    open_list = []
    closed_list = set()
    
    start_node = Node(start)
    goal_node = Node(goal)
    open_list.append(start_node)

    while open_list:
        open_list.sort(key=lambda node: node.f)
        current_node = open_list.pop(0)
        
        if current_node.position == goal_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]

        closed_list.add(current_node.position)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x, y = current_node.position[0] + dx, current_node.position[1] + dy
            if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0 and (x, y) not in closed_list:
                neighbor = Node((x, y), current_node)
                neighbor.g = current_node.g + 1
                neighbor.h = heuristic(neighbor.position, goal_node.position)
                neighbor.f = neighbor.g + neighbor.h
                
                if any(n.position == neighbor.position and n.f <= neighbor.f for n in open_list):
                    continue
                
                open_list.append(neighbor)
    
    return None

grid = [[0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0]]

start = (0, 0)
goal = (4, 4)

path = a_star(grid, start, goal)
print("Path found:", path if path else "No path found")