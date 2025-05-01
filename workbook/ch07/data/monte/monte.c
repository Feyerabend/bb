#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <time.h>
#include <stdbool.h>

#define N_NODES 10
#define INF INT_MAX

int graph[N_NODES][N_NODES];

void generate_random_graph(double p, int max_weight) {
    srand(time(NULL));
    // init all edges to infinity
    for (int i = 0; i < N_NODES; i++) {
        for (int j = 0; j < N_NODES; j++) {
            graph[i][j] = INF;
        }
    }
    
    // random edges
    for (int i = 0; i < N_NODES; i++) {
        for (int j = 0; j < N_NODES; j++) {
            if (i != j && (rand() / (double)RAND_MAX) < p) {
                graph[i][j] = rand() % max_weight + 1;
            }
        }
    }
}

// Monte Carlo shortest path algorithm
int monte_carlo_shortest_path(int start, int end, int n_samples) {
    int best_distance = INF;
    int best_path[N_NODES];
    int best_path_length = 0;
    
    for (int i = 0; i < n_samples; i++) {
        int visited[N_NODES] = {0};
        int path[N_NODES];
        int path_length = 0;
        int total_weight = 0;
        int current = start;
        
        path[path_length++] = current;
        visited[current] = 1;
        
        bool reached_end = false;
        
        // find a path until we reach end or get stuck
        while (current != end) {
            // find unvisited neighbors
            int neighbors[N_NODES], weights[N_NODES], count = 0;
            for (int j = 0; j < N_NODES; j++) {
                if (graph[current][j] != INF && !visited[j]) {
                    neighbors[count] = j;
                    weights[count] = graph[current][j];
                    count++;
                }
            }
            
            if (count == 0) break; // no unvisited neighbors, we're stuck
            
            // randomly select next node (possible: implement a weighted selection here)
            int next_index = rand() % count;
            int next_node = neighbors[next_index];
            
            // update path and total weight
            total_weight += weights[next_index];
            current = next_node;
            path[path_length++] = current;
            visited[current] = 1;
            
            // reached the end, record this path if it's better than what we've found
            if (current == end) {
                reached_end = true;
                break;
            }
            
            // to prevent too long paths, set a max path length
            if (path_length >= N_NODES) break;
        }
        
        // if reached the end and is better than our best so far, save it
        if (reached_end && total_weight < best_distance) {
            best_distance = total_weight;
            best_path_length = path_length;
            for (int j = 0; j < path_length; j++) {
                best_path[j] = path[j];
            }
        }
    }
    
    // print best path, if found
    if (best_distance != INF) {
        printf("Best path found: ");
        for (int i = 0; i < best_path_length; i++) {
            printf("%d", best_path[i]);
            if (i < best_path_length - 1) printf(" -> ");
        }
        printf("\n");
    }
    
    return (best_distance == INF) ? -1 : best_distance;
}

void print_graph() {
    printf("Graph adjacency matrix:\n");
    for (int i = 0; i < N_NODES; i++) {
        for (int j = 0; j < N_NODES; j++) {
            if (graph[i][j] == INF) {
                printf("INF ");
            } else {
                printf("%-3d ", graph[i][j]);
            }
        }
        printf("\n");
    }
}

int main() {
    generate_random_graph(0.3, 10);
    print_graph();
    
    int start = 0;
    int end = 9;
    int n_samples = 10000; // NB: increase number of samples for better chance of finding optimal path
    
    printf("Running Monte Carlo shortest path with %d samples...\n", n_samples);
    int shortest_distance = monte_carlo_shortest_path(start, end, n_samples);
    
    if (shortest_distance != -1) {
        printf("Estimated shortest path distance: %d\n", shortest_distance);
        printf("Note: This is an approximation, not guaranteed to be the absolute shortest path.\n");
    } else {
        printf("No path was found from %d to %d after %d attempts.\n", start, end, n_samples);
    }
    
    return 0;
}
