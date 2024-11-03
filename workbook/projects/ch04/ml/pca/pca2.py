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

class PCA:
    def __init__(self, n_components):
        self.n_components = n_components
        self.mean = None
        self.components = None
        self.eigenvalues = None

    def fit(self, X):
        # Step 1: Calculate the mean of X
        self.mean = [sum(feature) / len(X) for feature in zip(*X)]
        
        # Step 2: Center the data by subtracting the mean
        X_centered = [[x - m for x, m in zip(sample, self.mean)] for sample in X]

        # Step 3: Calculate the covariance matrix
        cov_matrix_calculator = CovarianceMatrix()
        cov_matrix_calculator.fit(X_centered)
        cov_matrix = cov_matrix_calculator.compute_covariance_matrix(X_centered)

        # Step 4: Compute eigenvalues and eigenvectors
        self.eigenvalues, eigenvectors = self._eigen_decomposition(cov_matrix)

        # Sort eigenvalues and eigenvectors
        sorted_indices = sorted(range(len(self.eigenvalues)), key=lambda k: self.eigenvalues[k], reverse=True)
        self.eigenvalues = [self.eigenvalues[i] for i in sorted_indices]
        self.components = [eigenvectors[i] for i in sorted_indices[:self.n_components]]

    def _eigen_decomposition(self, covariance_matrix):
        n = len(covariance_matrix)
        eigenvalues = [0] * n
        eigenvectors = [[0] * n for _ in range(n)]
        
        # Simplified characteristic polynomial for eigenvalue approximation
        for i in range(n):
            temp_matrix = [row[:] for row in covariance_matrix]
            temp_matrix[i][i] -= 1  # Start with lambda = 1
            det = self._determinant(temp_matrix)
            eigenvalues[i] = 1 / (det if det != 0 else 1e-10)

        # Compute eigenvectors using the eigenvalue
        for i in range(n):
            eigenvectors[i] = self._compute_eigenvector(covariance_matrix, eigenvalues[i])
        
        return eigenvalues, eigenvectors

    def _determinant(self, matrix):
        if len(matrix) == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        return 0

    def _compute_eigenvector(self, covariance_matrix, eigenvalue):
        vector = [0] * len(covariance_matrix)
        for i in range(len(covariance_matrix)):
            vector[i] = covariance_matrix[i][i] - eigenvalue
        return vector

    def transform(self, X):
        # Center the data using the mean
        X_centered = [[x - m for x, m in zip(sample, self.mean)] for sample in X]
        
        # Project the data onto the principal components
        transformed_data = []
        for sample in X_centered:
            transformed_sample = [sum(sample[j] * self.components[i][j] for j in range(len(sample))) for i in range(self.n_components)]
            transformed_data.append(transformed_sample)

        return transformed_data

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

    # Create PCA instance with 1 principal component
    pca = PCA(n_components=1)

    # Fit the PCA model
    pca.fit(X)

    # Transform the data
    transformed_data = pca.transform(X)

    # Print the transformed data
    print("Transformed Data:")
    for sample in transformed_data:
        print(sample)



from PIL import Image, ImageDraw

# Example original data points
original_data = [[2.5, 3.5], [1.5, 2.2], [2.3, 3.3], [5.1, 1.6], [3.5, 4.5]]  # Replace with your actual data
# Example PCA-transformed data (1D for simplicity)
pca_transformed_data = [1.30, -6.40, 1.68, -0.38, 3.79]  # Replace with your actual transformed data
labels = [0, 1, 0, 1, 0]  # Example binary labels (0 and 1)

# Image dimensions
width, height = 400, 400
image = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(image)

# Normalize original data for mapping to image coordinates
min_x = min(point[0] for point in original_data)
max_x = max(point[0] for point in original_data)
min_y = min(point[1] for point in original_data)
max_y = max(point[1] for point in original_data)

# Scale factors for original data
scale_x = width / (max_x - min_x)
scale_y = height / (max_y - min_y)

# Draw original data points in blue
for point, label in zip(original_data, labels):
    x = int((point[0] - min_x) * scale_x)
    y = height - int((point[1] - min_y) * scale_y)  # Invert Y-axis for image coordinates
    draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(0, 0, 255))  # Blue for original data

# Normalize PCA results for mapping to image coordinates
# Assuming transformed_data has been centered around 0
min_value = min(pca_transformed_data)
max_value = max(pca_transformed_data)

# Scale factors for PCA transformed data
scale_x_pca = width / (max_value - min_value)

# Draw PCA-transformed data points in red
for value, label in zip(pca_transformed_data, labels):
    x = int((value - min_value) * scale_x_pca)
    y = height // 2  # Center vertically for PCA points
    draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 0, 0))  # Red for PCA data

# Save or show the image
image.show()  # Use image.save("pca_visualization.png") to save