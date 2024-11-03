#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_POINTS 8  // Number of points in dataset

// Structure to represent a data point with x, y coordinates and a label
typedef struct {
    double x;
    double y;
    int label;  // 0 or 1 for binary classification
} Point;

// Structure to store distance and label information
typedef struct {
    double distance;
    int label;
} DistanceLabel;

// Function to calculate Euclidean distance between two points
double euclidean_distance(Point p1, Point p2) {
    return sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2));
}

// Comparator for sorting distances
int compare(const void *a, const void *b) {
    DistanceLabel *d1 = (DistanceLabel *)a;
    DistanceLabel *d2 = (DistanceLabel *)b;
    return (d1->distance > d2->distance) - (d1->distance < d2->distance);
}

// K-Nearest Neighbors function
int knn_classify(Point dataset[], int k, Point new_point) {
    DistanceLabel distances[NUM_POINTS];

    // Calculate distance from the new point to each point in the dataset
    for (int i = 0; i < NUM_POINTS; i++) {
        distances[i].distance = euclidean_distance(new_point, dataset[i]);
        distances[i].label = dataset[i].label;
    }

    // Sort the distances in ascending order
    qsort(distances, NUM_POINTS, sizeof(DistanceLabel), compare);

    // Count labels among the k nearest neighbors
    int count_label_0 = 0;
    int count_label_1 = 0;
    for (int i = 0; i < k; i++) {
        if (distances[i].label == 0) {
            count_label_0++;
        } else {
            count_label_1++;
        }
    }

    // Return the label with the highest count
    return (count_label_1 > count_label_0) ? 1 : 0;
}

int main() {
    // Example dataset with (x, y) points and labels
    Point dataset[NUM_POINTS] = {
        {1.0, 1.0, 0}, {2.0, 2.0, 0}, {3.0, 3.0, 0},
        {6.0, 6.0, 1}, {7.0, 7.0, 1}, {8.0, 8.0, 1},
        {9.0, 9.0, 1}, {5.0, 5.0, 0}
    };

    // New point to classify
    Point new_point = {4.0, 4.5};
    // Point new_point = {4.0, 6.5};

    // Number of neighbors to consider
    int k = 3;

    // Classify the new point
    int predicted_label = knn_classify(dataset, k, new_point);

    printf("Predicted label for the new point (%.1f, %.1f) is: %d\n", new_point.x, new_point.y, predicted_label);

    return 0;
}
