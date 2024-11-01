#include <stdio.h>
#include <float.h>
#include <math.h>

// Define the interval structure
typedef struct {
    double lower;
    double upper;
} Interval;

// Function to create an interval
Interval create_interval(double lower, double upper) {
    Interval i = { lower, upper };
    return i;
}

// Addition of two intervals
Interval add_intervals(Interval a, Interval b) {
    return create_interval(a.lower + b.lower, a.upper + b.upper);
}

// Subtraction of two intervals
Interval subtract_intervals(Interval a, Interval b) {
    return create_interval(a.lower - b.upper, a.upper - b.lower);
}

// Function to display an interval
void print_interval(Interval i) {
    printf("[%.2f, %.2f] hours\n", i.lower, i.upper);
}

int main() {
    // Define two time intervals in hours
    Interval event1 = create_interval(2.0, 3.0);   // Event duration between 2 to 3 hours
    Interval event2 = create_interval(1.0, 1.5);   // Event duration between 1 to 1.5 hours

    // Perform interval addition to find total duration if events are consecutive
    Interval total_duration = add_intervals(event1, event2);
    printf("Total duration if events are consecutive: ");
    print_interval(total_duration);

    // Perform interval subtraction to find the possible difference in time between events
    Interval time_difference = subtract_intervals(event1, event2);
    printf("Time difference between events: ");
    print_interval(time_difference);

    return 0;
}
