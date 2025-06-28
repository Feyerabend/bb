#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUM_STATES 3
#define SUNNY 0
#define CLOUDY 1
#define RAINY 2

// Transition matrix: [from_state][to_state]
double transition_matrix[NUM_STATES][NUM_STATES] = {
    // From SUNNY  to: SUNNY, CLOUDY, RAINY
    {0.7, 0.2, 0.1},
    // From CLOUDY to: SUNNY, CLOUDY, RAINY  
    {0.3, 0.4, 0.3},
    // From RAINY  to: SUNNY, CLOUDY, RAINY
    {0.2, 0.3, 0.5}
};

const char* state_names[] = {"Sunny", "Cloudy", "Rainy"};

int next_state(int current_state) {
    double rand_val = (double)rand() / RAND_MAX;
    double cumulative = 0.0;
    
    for (int i = 0; i < NUM_STATES; i++) {
        cumulative += transition_matrix[current_state][i];
        if (rand_val <= cumulative) {
            return i;
        }
    }
    return NUM_STATES - 1; // fallback
}

void simulate_weather(int days, int initial_state) {
    int current_state = initial_state;
    
    printf("Weather simulation for %d days:\n", days);
    printf("Day 0: %s\n", state_names[current_state]);
    
    for (int day = 1; day <= days; day++) {
        current_state = next_state(current_state);
        printf("Day %d: %s\n", day, state_names[current_state]);
    }
}

void calculate_stationary_distribution() {
    // Using power method to find stationary distribution
    double distribution[NUM_STATES] = {1.0/3, 1.0/3, 1.0/3}; // initial uniform
    double new_dist[NUM_STATES];
    
    // Iterate until convergence
    for (int iter = 0; iter < 1000; iter++) {
        for (int i = 0; i < NUM_STATES; i++) {
            new_dist[i] = 0.0;
            for (int j = 0; j < NUM_STATES; j++) {
                new_dist[i] += distribution[j] * transition_matrix[j][i];
            }
        }
        
        // Copy back
        for (int i = 0; i < NUM_STATES; i++) {
            distribution[i] = new_dist[i];
        }
    }
    
    printf("\nStationary distribution:\n");
    for (int i = 0; i < NUM_STATES; i++) {
        printf("%s: %.3f (%.1f%%)\n", state_names[i], distribution[i], 
               distribution[i] * 100);
    }
}

int main() {
    srand(time(NULL));
    
    printf("Weather Markov Chain Simulation\n");
    printf("================================\n\n");
    
    // Print transition matrix
    printf("Transition Matrix:\n");
    printf("         Sunny  Cloudy  Rainy\n");
    for (int i = 0; i < NUM_STATES; i++) {
        printf("%-8s", state_names[i]);
        for (int j = 0; j < NUM_STATES; j++) {
            printf("%6.2f", transition_matrix[i][j]);
        }
        printf("\n");
    }
    printf("\n");
    
    // Simulate weather
    simulate_weather(10, SUNNY);
    
    // Calculate long-term probabilities
    calculate_stationary_distribution();
    
    return 0;
}