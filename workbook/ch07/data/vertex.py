edges = [
    ("A", "B"),
    ("A", "C"),
    ("B", "D"),
    ("C", "D"),
    ("C", "E"),
    ("D", "E")
]

used = set()
cover = set()

for u, v in edges:
    if u not in used and v not in used:
        cover.add(u)
        cover.add(v)
        used.add(u)
        used.add(v)

print("Place cameras at intersections:", sorted(cover))

# Output the vertices where cameras should be placed
# This will ensure that all edges are covered by at least one camera
# The output will be a set of vertices where cameras should be placed
# to cover all edges in the graph.
# The vertices are sorted for better readability.
# The algorithm ensures that we cover all edges with the minimum number of cameras.
# The approach is greedy, selecting vertices that cover the most uncovered edges first.

# Iterates through edges one by one
# For each uncovered edge (u,v), if neither vertex is already in the cover:
# - Adds both endpoints u and v to the cover
# - Marks both as "used" so they won't be selected again

# Iteration 1: edge (A,B) - neither used
#  cover = {A, B}, used = {A, B}

# Iteration 2: edge (A,C) - A already used, skip
# Iteration 3: edge (B,D) - B already used, skip  
# Iteration 4: edge (C,D) - neither used
#  cover = {A, B, C, D}, used = {A, B, C, D}

# Iteration 5: edge (C,E) - C already used, skip
# Iteration 6: edge (D,E) - D already used, skip

# Final cover: {A, B, C, D}
