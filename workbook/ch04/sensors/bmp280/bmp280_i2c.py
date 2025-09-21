from machine import Pin, I2C
import time

# I2C configuration for Raspberry Pi Pico (I2C1)
i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)  # SCL: pin 10 (GPIO 7), SDA: pin 9 (GPIO 6)

# BMP280 address and registers
BME280_ADDR = 0x76  # Assuming SDO is grounded; change to 0x77 if SDO is connected to 3.3V

# Helpers to read signed/unsigned
def read_u8(addr): return int.from_bytes(i2c.readfrom_mem(BME280_ADDR, addr, 1), "little")
def read_s8(addr): return read_u8(addr) - 256 if read_u8(addr) > 127 else read_u8(addr)
def read_u16(addr): return int.from_bytes(i2c.readfrom_mem(BME280_ADDR, addr, 2), "little")
def read_s16(addr):
    val = read_u16(addr)
    return val if val < 32768 else val - 65536

# Verify chip ID
try:
    chip_id = read_u8(0xD0)
    if chip_id != 0x58:  # BMP280 ID is 0x58
        raise OSError("BMP280 not found, chip ID: 0x{:02X}".format(chip_id))
    print("BMP280 detected, chip ID: 0x{:02X}".format(chip_id))
except OSError as e:
    print("Failed to detect BMP280:", e)
    raise

# Read calibration data
try:
    dig_T1 = read_u16(0x88)
    dig_T2 = read_s16(0x8A)
    dig_T3 = read_s16(0x8C)
    dig_P1 = read_u16(0x8E)
    dig_P2 = read_s16(0x90)
    dig_P3 = read_s16(0x92)
    dig_P4 = read_s16(0x94)
    dig_P5 = read_s16(0x96)
    dig_P6 = read_s16(0x98)
    dig_P7 = read_s16(0x9A)
    dig_P8 = read_s16(0x9C)
    dig_P9 = read_s16(0x9E)
    print("Calibration data loaded")
except OSError as e:
    print("Error reading calibration data:", e)
    raise

# Set oversampling and mode (temp and pressure x1, normal mode)
i2c.writeto_mem(BME280_ADDR, 0xF4, bytes([0x27]))  # Temp/pressure oversampling x1, normal mode

t_fine = 0

def read_data():
    global t_fine
    try:
        data = i2c.readfrom_mem(BME280_ADDR, 0xF7, 6)  # Read 6 bytes for pressure and temperature
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

        # Temperature compensation
        var1 = (((adc_t >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
        var2 = (((((adc_t >> 4) - dig_T1) * ((adc_t >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
        t_fine = var1 + var2
        T = (t_fine * 5 + 128) >> 8

        # Pressure compensation
        var1 = t_fine - 128000
        var2 = var1 * var1 * dig_P6
        var2 = var2 + ((var1 * dig_P5) << 17)
        var2 = var2 + (dig_P4 << 35)
        var1 = ((var1 * var1 * dig_P3) >> 8) + ((var1 * dig_P2) << 12)
        var1 = (((1 << 47) + var1) * dig_P1) >> 33
        p = 1048576 - adc_p
        p = int((((p << 31) - var2) * 3125) // var1)
        var1 = (dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (dig_P8 * p) >> 19
        P = ((p + var1 + var2) >> 8) + (dig_P7 << 4)

        return T / 100.0, P / 25600.0
    except OSError as e:
        print("Error reading data:", e)
        raise

while True:
    try:
        temp, press = read_data()
        print("Temperature: %.2f °C  Pressure: %.2f hPa" % (temp, press))
    except OSError as e:
        print("Loop error:", e)
    time.sleep(1)
