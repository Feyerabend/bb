from machine import ADC, Pin
import time

# Constants
TEMP_SENSOR_PIN = 26  # ADC pin for the built-in temperature sensor
NUM_SAMPLES = 10       # Number of samples to collect for KNN

# Initialize variables
temperature_data = []  # Store sensed temperature readings

def read_temperature():
    # Read the ADC value from the built-in temperature sensor
    adc = ADC(Pin(TEMP_SENSOR_PIN))
    raw_value = adc.read_u16()  # Read raw ADC value
    # Convert ADC value to temperature in Celsius (this may vary based on your specific setup)
    # For the Raspberry Pi Pico, you might need to calibrate this conversion
    temperature = (raw_value / 65535) * 3.3 * 100  # Example conversion
    return temperature

def knn_predict(temperatures, new_temp, k=3):
    # Calculate the distances from new_temp to each recorded temperature
    distances = []
    
    for temp in temperatures:
        distance = abs(temp - new_temp)  # Simple absolute difference
        distances.append((distance, temp))  # Store distance and corresponding temperature

    # Sort distances and select the k nearest
    distances.sort(key=lambda x: x[0])
    k_nearest = distances[:k]

    # Calculate the mean of the k nearest temperatures
    prediction = sum(temp for _, temp in k_nearest) / k
    return prediction

while True:
    # Read the current temperature
    current_temperature = read_temperature()
    print("Sensed Temperature: {:.2f} °C".format(current_temperature))

    if len(temperature_data) > 0:
        # Predict temperature if we have enough data
        predicted_temperature = knn_predict(temperature_data, current_temperature)
        print("Predicted Temperature: {:.2f} °C".format(predicted_temperature))
    else:
        print("Not enough data for prediction.")

    # Add the sensed temperature to the dataset
    temperature_data.append(current_temperature)

    # Limit the size of the dataset to the last NUM_SAMPLES
    if len(temperature_data) > NUM_SAMPLES:
        temperature_data.pop(0)  # Keep only the latest samples

    # Wait before the next reading
    time.sleep(5)  # Delay for 5 seconds (adjust as necessary)
