
## Kalman filter

Here's a simple example of using a Kalman filter in MicroPython to *smooth out* a list of
temperature measurements. This can help reduce noise in the measurements, providing a more
stable temperature reading.

The *Kalman filter* is an iterative algorithm that estimates the true value of a variable
(like temperature) by considering both the measurement and the estimated previous state.
It's widely used in embedded systems for filtering noisy sensor data.


# Kalman filter for temperature readings in MicroPython

```python
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
```


### Explanation of the Code

1.	KalmanFilter Class: This class initializes with parameters for process noise,
    measurement noise, estimated error, and an initial value.
	- process_variance: Represents the uncertainty in the process (e.g., how much
      we expect the temperature might naturally vary).
	- measurement_variance: Represents the noise in the temperature measurements.
	- estimated_error: The initial guess for the error in the estimate.

2.	Update Function: Each time a new temperature measurement is read, we call update,
    which:
	- Calculates the Kalman gain based on the current estimate and the measurement
      variance.
	- Updates the current estimate by blending the previous estimate and the new
      measurement based on the Kalman gain.
	- Adjusts the estimated error for the next iteration.

3.	Example Usage: The code then applies this filter to a list of temperature
    measurements and prints both the raw and filtered values for each reading.


### Example Output

For a list of temperature readings, you'd see an output like this:

```shell
Raw temperature: 22.1 Filtered temperature: 22.1
Raw temperature: 22.5 Filtered temperature: 22.3
Raw temperature: 23.0 Filtered temperature: 22.6
Raw temperature: 22.8 Filtered temperature: 22.7
...
```

This Kalman filter helps smooth out the noise, giving a more stable reading for
applications where precise temperature control is needed.
