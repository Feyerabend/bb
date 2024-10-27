import machine
import utime

# set up ADC to read from onboard temperature sensor
sensor_temp = machine.ADC(4)

# conversion factor to convert raw ADC value to voltage (3.3V / 65535)
conversion_factor = 3.3 / (65535)

while True:
    # read raw temperature sensor value (0-65535)
    reading = sensor_temp.read_u16()

    # convert raw value to voltage
    voltage = reading * conversion_factor

    # voltage to Celsius temperature based on onboard sensor
    celsius = 27 - (voltage - 0.706) / 0.001721

    # Celsius to Fahrenheit
    fahrenheit = celsius * 9 / 5 + 32

    # print temperature in both Celsius and Fahrenheit
    print("Temperature: {:.2f} C / {:.2f} F".format(celsius, fahrenheit))

    # wait before reading again
    utime.sleep(2)
