from PIL import Image, ImageDraw
import numpy as np

# Function to normalize the dataset
def normalize(X):
    X = np.array(X)
    return (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))

class SVM:
    def __init__(self, learning_rate=0.01, lambda_param=0.01, n_iters=1000):
        self.lr = learning_rate
        self.lambda_param = lambda_param
        self.n_iters = n_iters
        self.w = None
        self.b = None

    def fit(self, X, y):
        n_samples, n_features = X.shape
        # Initialize weights and bias
        self.w = np.zeros(n_features)
        self.b = 0.0
        
        for _ in range(self.n_iters):
            for idx in range(n_samples):
                x_i = X[idx]
                condition = y[idx] * (self._predict(x_i) >= 1)
                if condition:
                    # Correct classification
                    self.w = (1 - self.lr * self.lambda_param) * self.w
                else:
                    # Misclassified
                    self.w += self.lr * (y[idx] * x_i - 2 * self.lambda_param * self.w)
                    self.b += self.lr * y[idx]

    def _predict(self, x):
        return np.dot(x, self.w) + self.b

    def predict(self, X):
        return [1 if self._predict(x) >= 0 else -1 for x in X]

# Sample data points
X = np.array([[3.1, 2.5], [1.5, 2.2], [2.3, 3.3], [5.1, 1.6], [4.0, 2.0], [0.5, 0.8]])
y = np.array([1, 1, -1, -1, 1, -1])

# Normalize the feature matrix for display purposes
X_min = X.min(axis=0)
X_max = X.max(axis=0)
X_normalized = (X - X_min) / (X_max - X_min)  # Normalize to [0, 1]

# Create an image
width, height = 400, 400
image = Image.new("RGB", (width, height), (255, 255, 255))  # White background
draw = ImageDraw.Draw(image)

# Create a mesh grid for plotting the decision boundary
xx, yy = np.meshgrid(np.linspace(0, 1, 400), np.linspace(0, 1, 400))

# Define a simple linear decision boundary for visualization
# This should be based on your SVM's coefficients in a real case
# For demonstration, let's create a hypothetical linear decision boundary
Z = np.where((xx + yy) > 1, 1, -1)  # Adjust as necessary for your actual SVM

# Draw the decision boundary
for i in range(Z.shape[0]):
    for j in range(Z.shape[1]):
        if Z[i, j] == 1:
            draw.point((j, i), fill=(200, 200, 255))  # Light blue for class 1
        else:
            draw.point((j, i), fill=(255, 200, 200))  # Light red for class -1

# Plot the data points
for point, label in zip(X_normalized, y):
    x, y = point * [width, height]  # Scale back to image coordinates
    if label == 1:
        draw.ellipse((x-5, y-5, x+5, y+5), fill=(0, 0, 255), outline=(0, 0, 0))  # Blue circle for class 1
    else:
        draw.ellipse((x-5, y-5, x+5, y+5), fill=(255, 0, 0), outline=(0, 0, 0))  # Red circle for class -1

# Save or show the image
image.show()  # Display the image
# image.save("svm_decision_boundary.png")  # Optionally save the image