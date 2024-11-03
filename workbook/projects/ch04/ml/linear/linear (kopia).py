class LinearRegression:
    def __init__(self):
        self.m = 0  # Slope
        self.b = 0  # Intercept

    def fit(self, X, y):
        n = len(X)  # Number of data points
        if n == 0:
            return
        
        # Calculate the means of x and y
        mean_x = sum(X) / n
        mean_y = sum(y) / n
        
        # Calculate the slope (m) and intercept (b)
        numerator = sum((X[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = sum((X[i] - mean_x) ** 2 for i in range(n))
        
        self.m = numerator / denominator if denominator != 0 else 0
        self.b = mean_y - self.m * mean_x

    def predict(self, X):
        return [self.m * x + self.b for x in X]

# Example usage:
if __name__ == "__main__":
    # Sample data
    X = [1, 2, 3, 4, 5]  # Features
    y = [2, 3, 5, 7, 11]  # Labels

    # Create and train the model
    model = LinearRegression()
    model.fit(X, y)

    # Make predictions
    predictions = model.predict([6, 7, 8])
    
    for x, prediction in zip([6, 7, 8], predictions):
        print(f"Predicted value for {x}: {prediction}")