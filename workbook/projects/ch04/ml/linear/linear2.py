class LinearRegression:
    def __init__(self):
        self.weights = None
        self.intercept = 0

    def fit(self, X, y):
        n = len(X)
        # Adding a bias column (intercept) to the feature matrix
        X_b = [[1] + list(x) for x in X]  # Adding a column of ones for the intercept
        X_transpose = [[X_b[j][i] for j in range(n)] for i in range(len(X_b[0]))]  # Transpose of X_b

        # Calculate the weights using the Normal Equation: (X^T * X)^(-1) * X^T * y
        XTX = [[sum(X_transpose[i][k] * X_b[k][j] for k in range(n)) for j in range(len(X_b[0]))] for i in range(len(X_b[0]))]
        XTy = [sum(X_transpose[i][k] * y[k] for k in range(n)) for i in range(len(X_b[0]))]

        XTX_inv = self.inv(XTX)  # Inverse of XTX
        if XTX_inv is None:
            raise ValueError("Matrix inversion failed.")

        self.weights = [sum(XTX_inv[i][j] * XTy[j] for j in range(len(XTy))) for i in range(len(XTX_inv))]

    def inv(self, matrix):
        """ Inverts a matrix using Gauss-Jordan elimination """
        n = len(matrix)
        # Augment the matrix with the identity matrix
        augmented = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(matrix)]
        
        for i in range(n):
            # Make the diagonal contain all 1's
            diag_val = augmented[i][i]
            if diag_val == 0:
                return None  # Singular matrix, can't invert
            for j in range(2 * n):
                augmented[i][j] /= diag_val
            
            # Make all rows below this one 0 in current column
            for j in range(i + 1, n):
                factor = augmented[j][i]
                for k in range(2 * n):
                    augmented[j][k] -= factor * augmented[i][k]

        # Back substitution
        for i in range(n - 1, -1, -1):
            for j in range(i - 1, -1, -1):
                factor = augmented[j][i]
                for k in range(2 * n):
                    augmented[j][k] -= factor * augmented[i][k]

        # Extract the inverted matrix
        inverted_matrix = [row[n:] for row in augmented]
        return inverted_matrix

    def predict(self, X):
        # Make predictions with weights and intercept
        predictions = []
        for x in X:
            # Predictions based on weights and intercept
            pred = self.weights[0] + sum(w * feature for w, feature in zip(self.weights[1:], x))
            predictions.append(pred)
        return predictions


class SmartGreenhouse:
    def __init__(self):
        self.model = LinearRegression()
        self.temperature_data = []  # Historical temperature readings
        self.humidity_data = []     # Historical humidity readings
        self.growth_data = []       # Corresponding plant growth data

    def collect_data(self, temperature, humidity, growth):
        self.temperature_data.append(temperature)
        self.humidity_data.append(humidity)
        self.growth_data.append(growth)

    def train_model(self):
        # Combine temperature and humidity into feature matrix
        X = list(zip(self.temperature_data, self.humidity_data))
        self.model.fit(X, self.growth_data)

    def predict_growth(self, temperature, humidity):
        # Use both temperature and humidity for prediction
        return self.model.predict([[temperature, humidity]])


# Example usage
greenhouse = SmartGreenhouse()

# Simulate data collection
greenhouse.collect_data(20, 50, 15)  # Day 1
greenhouse.collect_data(22, 55, 20)  # Day 2
greenhouse.collect_data(21, 53, 18)  # Day 3

# Train the model
greenhouse.train_model()

# Predict growth for new conditions
predicted_growth = greenhouse.predict_growth(24, 60)
print(f"Predicted plant growth: {predicted_growth[0]}")