import math
import numpy as np

class PCA:
    def __init__(self, n_components):
        self.n_components = n_components
        self.mean = None
        self.components = None

    def fit(self, X):
        # Step 1: Standardize the data
        self.mean = np.mean(X, axis=0)
        X_centered = X - self.mean

        # Step 2: Calculate the covariance matrix
        covariance_matrix = np.cov(X_centered, rowvar=False)

        # Step 3: Calculate the eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

        # Step 4: Sort eigenvalues and eigenvectors
        sorted_indices = np.argsort(eigenvalues)[::-1]
        self.components = eigenvectors[:, sorted_indices[:self.n_components]]

    def transform(self, X):
        X_centered = X - self.mean
        return np.dot(X_centered, self.components)

# Example Usage
if __name__ == "__main__":
    # Sample data
    X = np.array([[2.5, 2.4],
                  [0.5, 0.7],
                  [2.2, 2.9],
                  [1.9, 2.2],
                  [3.1, 3.0],
                  [2.3, 2.7],
                  [2, 1.6],
                  [1, 1.1],
                  [1.5, 1.6],
                  [1.1, 0.9]])

    # Create PCA instance
    pca = PCA(n_components=1)

    # Fit the model
    pca.fit(X)

    # Transform the data
    X_transformed = pca.transform(X)

    print("Original Data:")
    print(X)
    print("Transformed Data:")
    print(X_transformed)