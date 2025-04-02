import random

def generate_random_graph(n_nodes=10, p=0.3, weight_range=(1, 10)):
    graph = {node: {} for node in range(n_nodes)}
    nodes = list(range(n_nodes))
    random.shuffle(nodes)

    # spanning tree to ensure connectivity
    for i in range(1, n_nodes):
        j = random.randint(0, i-1)
        weight = random.randint(*weight_range)
        u, v = nodes[i], nodes[j]
        graph[u][v] = graph[v][u] = weight

    # extra edges with probability p
    for u in range(n_nodes):
        for v in range(u+1, n_nodes):
            if v not in graph[u] and random.random() < p:
                weight = random.randint(*weight_range)
                graph[u][v] = graph[v][u] = weight

    return graph

def print_graph(graph):
    print("\nGenerated Graph (Adjacency List with Weights):")
    for node, edges in graph.items():
        edge_list = ", ".join(f"{neighbor}({weight})" for neighbor, weight in edges.items())
        print(f"  {node}: {edge_list}")
    print()

def monte_carlo_shortest_path(graph, start, end, n_samples=1000):
    best_distance = float('inf')
    successful_paths = 0

    print(f"Starting Monte Carlo search from {start} to {end} with {n_samples} samples...\n")

    for sample in range(n_samples):
        current = start
        total_weight = 0
        visited = {current}
        path = [current]

        while current != end:
            neighbors = [n for n in graph[current] if n not in visited]
            if not neighbors:
                break  # dead end

            next_node = random.choice(neighbors)
            total_weight += graph[current][next_node]

            if total_weight >= best_distance:
                break  # early exit, if path is already too long

            visited.add(next_node)
            path.append(next_node)
            current = next_node

        if current == end:
            successful_paths += 1
            if total_weight < best_distance:
                best_distance = total_weight
                print(f"  New best path found ({sample + 1}): {path} with weight {total_weight}")

    if best_distance == float('inf'):
        print("\nNo valid path found.")
        return None

    print(f"\nTotal successful paths: {successful_paths}/{n_samples}")
    print(f"Estimated shortest path weight: {best_distance}")
    return best_distance


G = generate_random_graph(n_nodes=10, p=0.3)
print_graph(G)
print("Final Result:", monte_carlo_shortest_path(G, 0, 9, n_samples=1000))
