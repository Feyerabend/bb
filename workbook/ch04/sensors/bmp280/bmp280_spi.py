from machine import Pin, SPI
import time

# SPI configuration for Raspberry Pi Pico (SPI1)
cs = Pin(22, Pin.OUT)  # Chip Select on physical pin 30 (GPIO 22)
spi = SPI(1, baudrate=500000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=Pin(12))  # SCK: pin 14 (GPIO 10), MOSI: pin 15 (GPIO 11), MISO: pin 16 (GPIO 12)

# BMP280 address and registers
BMP280_ADDR = 0x76  # Assuming SDO is grounded; change to 0x77 if SDO is connected to 3.3V
REG_ID = 0xD0
REG_CONFIG = 0xF5
REG_CTRL_MEAS = 0xF4
REG_DATA = 0xF7
REG_CALIB = 0x88

# Helper functions for SPI communication
def read_reg(reg, nbytes=1):
    cs.value(0)  # Select chip
    try:
        spi.write(bytes([reg | 0x80]))  # Set read bit
        data = spi.read(nbytes)
        return data
    except OSError as e:
        print("SPI read error:", e)
        raise
    finally:
        cs.value(1)  # Deselect chip

def write_reg(reg, data):
    cs.value(0)  # Select chip
    try:
        spi.write(bytes([reg & 0x7F]))  # Clear read bit
        spi.write(bytes(data))
    except OSError as e:
        print("SPI write error:", e)
        raise
    finally:
        cs.value(1)  # Deselect chip

# Helpers to read signed/unsigned
def read_u8(addr): return int.from_bytes(read_reg(addr, 1), "little")
def read_s8(addr): return read_u8(addr) - 256 if read_u8(addr) > 127 else read_u8(addr)
def read_u16(addr): return int.from_bytes(read_reg(addr, 2), "little")
def read_s16(addr):
    val = read_u16(addr)
    return val if val < 32768 else val - 65536

# Verify chip ID
try:
    chip_id = read_u8(REG_ID)
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
write_reg(REG_CONFIG, [0x00])  # Standby time and filter
write_reg(REG_CTRL_MEAS, [0x27])  # Temp/pressure oversampling x1, normal mode

t_fine = 0

def read_data():
    global t_fine
    try:
        data = read_reg(REG_DATA, 6)  # Read 6 bytes for pressure and temperature
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