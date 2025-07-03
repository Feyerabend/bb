
## K-means

K-means clustering is an algorithm that groups data points into a specified number of clusters
by finding the best positions for cluster centers. The basic idea is to minimise the total
distance between each data point and its nearest cluster center.

The algorithm starts by randomly placing K cluster centers (centroids) in your data space.
Then it repeatedly performs two main steps until the centroids stop moving significantly.
First, it assigns each data point to whichever centroid is closest to it, creating K groups.
Second, it recalculates each centroid's position by moving it to the average location of all
points assigned to that cluster.

This process continues iteratively because moving the centroids changes which points should
be assigned to which clusters, and reassigning points changes where the centroids should be
positioned. Eventually, the system reaches a stable state where the centroids don't move much
between iterations, meaning the algorithm has converged on a solution.

The "means" in K-means refers to this averaging process where centroids are positioned at the
mean (average) location of their assigned points. The algorithm is trying to find cluster
centers that minimise the sum of squared distances from each point to its assigned centroid,
which makes the clusters as compact as possible.

One important thing to understand is that K-means will always find K clusters, even if the data
doesn't naturally form that many groups. It's also sensitive to the initial placement of
centroids, which is why the algorithm is often run multiple times with different starting
positions to find the best solution.

