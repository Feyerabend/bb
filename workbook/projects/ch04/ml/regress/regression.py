import machine
import time

# Pin configuration for onboard temperature sensor (GPIO28)
adc_temp = machine.ADC(4)  # GPIO28 maps to ADC4 in Pico
# Internal temperature sensor has a built-in reference voltage of 3.3V, and it maps 0-3.3V to a range of 0-65535 (12-bit ADC)
# The formula to convert the raw ADC value to Celsius is:
# temperature = (temperature_raw / 65536) * 3.3 * 100 - 50
# where 65536 is the range of the 12-bit ADC, and 3.3 is the reference voltage

# Parameters for temperature collection and regression
temperature_data = []
time_data = []
max_data_points = 20  # Limit of historical data points to store

# Function to read the temperature from the onboard sensor
def read_temperature():
    raw = adc_temp.read_u16()  # Read ADC value (range 0-65535)
    # Convert the raw ADC value to temperature (Celsius)
    temperature = (raw / 65536) * 3.3 * 100 - 50
    return temperature

# Function to perform linear regression
def linear_regression(x, y):
    n = len(x)
    if n == 0:
        return 0, 0  # Avoid division by zero if no data is available

    # Calculate means of x and y
    mean_x = sum(x) / n
    mean_y = sum(y) / n

    # Calculate the slope (m) and intercept (b)
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0, mean_y  # If all x-values are the same, we cannot compute the slope
    
    m = numerator / denominator
    b = mean_y - m * mean_x
    return m, b

# Function to predict the temperature based on the regression model
def predict_temperature(m, b, time_point):
    return m * time_point + b

# Main loop to collect data and perform regression
for t in range(1, 101):  # Simulate 100 time points (1-100)
    # Read temperature from onboard sensor
    temperature = read_temperature()
    
    # Store time and temperature data
    temperature_data.append(temperature)
    time_data.append(t)
    
    # Keep the data set small to avoid memory overflow
    if len(temperature_data) > max_data_points:
        temperature_data.pop(0)
        time_data.pop(0)
    
    # Perform linear regression on the collected data
    m, b = linear_regression(time_data, temperature_data)
    
    # Predict the next temperature value based on the regression
    predicted_temp = predict_temperature(m, b, t + 1)  # Predict next time point
    
    # Print current temperature and prediction
    print(f"Time: {t} min, Current Temp: {temperature:.2f}°C, Predicted Temp (next): {predicted_temp:.2f}°C")
    
    # Wait for a while before collecting the next reading
    time.sleep(10)  # 10 seconds interval
