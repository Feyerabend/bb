A simple implementation of the K-Nearest Neighbors (KNN) algorithm in C, along with a basic example application.

Overview of K-Nearest Neighbors (KNN)

The KNN algorithm is a simple, non-parametric algorithm used for classification and regression. Given a data point, KNN finds the k closest points in the dataset and uses them to predict the class or value of that point.

Example Application

Let’s implement KNN for a binary classification task. We’ll use a small dataset of points in a 2D space, labeled as either 0 or 1. Given a new point, the algorithm will classify it based on the majority label of its k nearest neighbors.

KNN Implementation in C

Here’s a basic implementation of KNN in C with Euclidean distance:

```c
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

    // Number of neighbors to consider
    int k = 3;

    // Classify the new point
    int predicted_label = knn_classify(dataset, k, new_point);

    printf("Predicted label for the new point (%.1f, %.1f) is: %d\n", new_point.x, new_point.y, predicted_label);

    return 0;
}
```

Explanation of the Code

	1.	Data Structures:
	•	Point: Represents a point in 2D space with coordinates (x, y) and a binary label 0 or 1.
	•	DistanceLabel: Stores the distance from a point to the new point and the label of that point.
	2.	Euclidean Distance Calculation:
	•	euclidean_distance() calculates the Euclidean distance between two points.
	3.	Sorting by Distance:
	•	qsort() is used to sort the array of distances in ascending order based on their distance from the new point.
	4.	Majority Voting:
	•	The nearest k neighbors are counted based on their label, and the label with the majority count is returned as the prediction.

Example Output

Running the program will classify the new point (4.0, 4.5) based on its 3 nearest neighbors from the dataset. If the majority of the nearest neighbors have the label 0, the output will be 0; otherwise, it will be 1.

Notes

	•	This is a simple, unoptimized version of KNN suitable for small datasets.
	•	In practice, KNN can be computationally expensive for large datasets since it requires calculating distances to all points in the dataset.
