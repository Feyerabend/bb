import numpy as np

# Hardcoded daily average temperatures (in Celsius) for Uppsala
# December 2024 (used for training)

dec_2022 = [
    -3.0, -3.5, -3.2, -3.0, -3.1, -3.3, -3.4, -3.2, -3.0, -2.8, 
    -2.7, -2.6, -2.5, -2.4, -2.3, -2.2, -2.1, -2.0, -1.9, -1.8, 
    -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0, -0.9, -0.8, -0.7
]

dec_2024 = [
    -2.1, -1.8, -2.5, -3.0, -2.0, -1.2, -1.0, -1.5, -2.3, -1.7,
    -1.1, -0.8, -0.5, -0.2,  0.1,  0.3, -0.1, -0.5, -1.3, -1.7,
    -2.0, -1.5, -1.2, -1.0, -0.7, -0.3, -0.8, -1.1, -1.6, -2.2, -2.5
]

# January 2025 (used for evaluation)
jan_2025_actual = [
    -3.0, -3.2, -2.8, -2.5, -2.3, -2.0, -1.8, -1.5, -1.7, -2.0,
    -2.2, -2.4, -2.7, -2.9, -3.1, -3.3, -3.5, -3.0, -2.8, -2.5,
    -2.2, -2.0, -1.8, -1.6, -1.4, -1.2, -1.0, -0.8, -0.6, -0.5, -0.3
]

# Normalize data using min-max from training set only
min_temp, max_temp = min(dec_2024), max(dec_2024)
normalize = lambda t: (t - min_temp) / (max_temp - min_temp)
denormalize = lambda t: t * (max_temp - min_temp) + min_temp

dec_normalized = [normalize(t) for t in dec_2024]
jan_normalized_actual = [normalize(t) for t in jan_2025_actual]

# Prepare training sequences
sequence_length = 5
X_train, Y_train = [], []
for i in range(len(dec_normalized) - sequence_length):
    X_train.append(dec_normalized[i:i + sequence_length])
    Y_train.append(dec_normalized[i + sequence_length])
X_train, Y_train = np.array(X_train), np.array(Y_train)

# Define a simple RNN
class SimpleRNN:
    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.Wxh = np.random.randn(hidden_size, input_size) * 0.01
        self.Whh = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Why = np.random.randn(1, hidden_size) * 0.01
        self.h = np.zeros((hidden_size,))

    def step(self, x):
        self.h = np.tanh(np.dot(self.Wxh, x) + np.dot(self.Whh, self.h))
        y = np.dot(self.Why, self.h)
        return y[0]

# Train the RNN
rnn = SimpleRNN(input_size=sequence_length, hidden_size=10)
learning_rate = 0.01
epochs = 100

for epoch in range(epochs):
    total_loss = 0
    for x, y_true in zip(X_train, Y_train):
        y_pred = rnn.step(x)
        loss = (y_pred - y_true) ** 2
        total_loss += loss
        dL_dy = 2 * (y_pred - y_true)
        dL_dWhy = dL_dy * rnn.h
        dL_dh = dL_dy * rnn.Why.flatten()
        rnn.Why -= learning_rate * dL_dWhy.reshape(1, -1)
        rnn.Wxh -= learning_rate * np.outer(dL_dh, x)
        rnn.Whh -= learning_rate * np.outer(dL_dh, rnn.h)
    if epoch % 20 == 0:
        print(f"Epoch {epoch}, Loss: {total_loss:.4f}")

# Predict January temperatures
predictions = []
context = dec_normalized[-sequence_length:]  # start from last 5 days in December
for _ in range(len(jan_2025_actual)):
    pred = rnn.step(np.array(context))
    predictions.append(pred)
    context = np.append(context[1:], pred)

# Denormalize predictions
jan_predicted = [denormalize(p) for p in predictions]
jan_actual = jan_2025_actual

# Generate simple ASCII visualization
ascii_chart = []
for i, (actual, pred) in enumerate(zip(jan_actual, jan_predicted)):
    a_pos = int((actual + 5) * 3)  # scale for visualization
    p_pos = int((pred + 5) * 3)
    line = [" "] * 40
    if 0 <= a_pos < len(line):
        line[a_pos] = "A"
    if 0 <= p_pos < len(line):
        line[p_pos] = "P" if line[p_pos] == " " else "*"
    ascii_chart.append(f"Day {i+1:2d}: " + "".join(line) + f"  ({actual:.1f}°C vs {pred:.1f}°C)")

ascii_output = "\n".join(ascii_chart)

# Output visualization and a sample comparison of predictions vs actuals
print(ascii_output[:1000])  # limit output for display here