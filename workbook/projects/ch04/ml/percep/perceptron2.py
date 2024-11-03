from PIL import Image, ImageDraw

class Perceptron:
    def __init__(self, learning_rate=0.1, n_iters=1000):
        self.lr = learning_rate
        self.n_iters = n_iters
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        n_samples, n_features = len(X), len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0
        
        for _ in range(self.n_iters):
            for idx, x_i in enumerate(X):
                linear_output = sum(w * x for w, x in zip(self.weights, x_i)) + self.bias
                y_predicted = self._activation_function(linear_output)

                # Update weights and bias
                update = self.lr * (y[idx] - y_predicted)
                self.weights = [w + update * x for w, x in zip(self.weights, x_i)]
                self.bias += update

    def _activation_function(self, x):
        return 1 if x >= 0 else 0

    def predict(self, X):
        linear_output = [sum(w * x for w, x in zip(self.weights, x_i)) + self.bias for x_i in X]
        return [self._activation_function(x) for x in linear_output]

# Sample data points (replace these with your actual data)
X = [[0.1, 0.2], [0.2, 0.1], [0.3, 0.4], [0.8, 0.9]]  # Example feature data
predictions = [0, 0, 0, 1]  # Your predictions

# Define the size of the image
img_width, img_height = 400, 400
image = Image.new("RGB", (img_width, img_height), "white")
draw = ImageDraw.Draw(image)

# Map predictions to colors
colors = ['blue' if p == 0 else 'red' for p in predictions]

# Scale and draw points on the image
for (x, y), prediction in zip(X, predictions):
    # Scale the coordinates to fit the image dimensions
    scaled_x = int(x * img_width)
    scaled_y = int(y * img_height)
    
    # Draw the point on the image
    draw.ellipse((scaled_x - 5, scaled_y - 5, scaled_x + 5, scaled_y + 5), fill=colors[prediction])

# Save or show the image
image.show()  # To display the image
# image.save("perceptron_predictions.png")  # To save the image
