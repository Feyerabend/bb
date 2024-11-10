class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, estimated_error, initial_value=0):
        self.process_variance = process_variance  # process noise
        self.measurement_variance = measurement_variance  # measurement noise
        self.estimated_error = estimated_error  # initial estimated error
        self.value = initial_value  # initial estimated value
        self.kalman_gain = 0  # initial Kalman gain

    def update(self, measurement):
        # update Kalman gain
        self.kalman_gain = self.estimated_error / (self.estimated_error + self.measurement_variance)
        
        # update estimate with measurement
        self.value = self.value + self.kalman_gain * (measurement - self.value)
        
        # update estimated error
        self.estimated_error = (1 - self.kalman_gain) * self.estimated_error + abs(self.value) * self.process_variance

        return self.value

# example list of noisy temperature measurements
temperature_measurements = [22.1, 22.5, 23.0, 22.8, 23.3, 23.5, 23.2, 23.7, 24.0, 23.9]

# Kalman filter parameters
process_variance = 1e-3  # small process noise
measurement_variance = 0.1  # assume some measurement noise
initial_estimated_error = 1.0  # initial error in estimation

# init Kalman filter
kf = KalmanFilter(process_variance, measurement_variance, initial_estimated_error, initial_value=temperature_measurements[0])

# apply Kalman filter to temperature measurements
filtered_temperatures = []

for measurement in temperature_measurements:
    filtered_temp = kf.update(measurement)
    filtered_temperatures.append(filtered_temp)
    print("Raw temperature:", measurement, "Filtered temperature:", filtered_temp)
