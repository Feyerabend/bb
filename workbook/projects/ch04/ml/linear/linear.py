

class LinearRegression:
    def __init__(self):
        self.slope = 0
        self.intercept = 0

    def fit(self, X, y):
        n = len(X)
        mean_x = sum(x[0] for x in X) / n  # Calculate mean of first feature
        mean_y = sum(y) / n  # Calculate mean of target values

        # Calculate slope (m) and intercept (b) using least squares
        num = sum((x[0] - mean_x) * (y[i] - mean_y) for i, x in enumerate(X))
        den = sum((x[0] - mean_x) ** 2 for x in X)
        self.slope = num / den
        self.intercept = mean_y - self.slope * mean_x

    def predict(self, x):
        return self.slope * x + self.intercept

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
        # Use the first feature (temperature) for prediction
        return self.model.predict(temperature)

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
print(f"Predicted plant growth: {predicted_growth}")
