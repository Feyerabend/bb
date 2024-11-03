class CovarianceMatrix:
    def __init__(self):
        self.mean = None

    def fit(self, X):
        # Calculate the mean of each column
        self.mean = [sum(column) / len(column) for column in zip(*X)]

    def compute_covariance_matrix(self, X):
        n_samples = len(X)
        n_features = len(X[0])

        # Initialize the covariance matrix with zeros
        covariance_matrix = [[0] * n_features for _ in range(n_features)]

        # Calculate the covariance
        for i in range(n_features):
            for j in range(n_features):
                covariance_sum = 0
                for sample in X:
                    covariance_sum += (sample[i] - self.mean[i]) * (sample[j] - self.mean[j])
                covariance_matrix[i][j] = covariance_sum / (n_samples - 1)  # Use (n - 1) for sample covariance

        return covariance_matrix

# Example Usage
if __name__ == "__main__":
    # Sample data (5 samples with 2 features each)
    X = [
        [2.5, 2.4],
        [0.5, 0.7],
        [2.2, 2.9],
        [1.9, 2.2],
        [3.1, 3.0]
    ]

    # Create CovarianceMatrix instance
    covariance_matrix_calculator = CovarianceMatrix()

    # Fit the model to calculate mean
    covariance_matrix_calculator.fit(X)

    # Compute the covariance matrix
    covariance_matrix = covariance_matrix_calculator.compute_covariance_matrix(X)

    # Print the covariance matrix
    print("Covariance Matrix:")
    for row in covariance_matrix:
        print(row)
