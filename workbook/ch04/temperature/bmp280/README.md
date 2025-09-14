
## Temperature from BMP280

Here are examples how to handle e.g. temperature measurements with BMP280, without
resorting to using external libraires. Only proceed with the "raw metal":
- Manually read calibration registers.
- Apply Bosch’s compensation formula from the datasheet.


### MicroPython (no external libs)

Handle the chip directly on the Pico via SPI.

```python
from machine import Pin, SPI
import time

# BMP280 SPI setup
CS_PIN = Pin(8, Pin.OUT, value=1)  # GPIO 8 (Physical Pin 11)
spi = SPI(1, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB,
          sck=Pin(10), mosi=Pin(11), miso=Pin(12))  # SPI1: Pins 14, 15, 16

# BMP280 register addresses
REG_DIG_T1 = 0x88
REG_CTRL_MEAS = 0xF4
REG_TEMP = 0xFA

# SPI read/write functions
def read_reg(reg, num_bytes):
    CS_PIN.value(0)  # Select chip
    spi.write(bytes([reg | 0x80]))  # Read mode (MSB=1)
    data = spi.read(num_bytes)
    CS_PIN.value(1)  # Deselect chip
    return data

def write_reg(reg, data):
    CS_PIN.value(0)  # Select chip
    spi.write(bytes([reg & 0x7F]))  # Write mode (MSB=0)
    spi.write(bytes([data]))
    CS_PIN.value(1)  # Deselect chip

# Read an unsigned short (little endian)
def read_u16(reg):
    d = read_reg(reg, 2)
    return d[0] | (d[1] << 8)

# Read a signed short
def read_s16(reg):
    val = read_u16(reg)
    return val if val < 32768 else val - 65536

# Get calibration data for temperature
dig_T1 = read_u16(REG_DIG_T1)
dig_T2 = read_s16(REG_DIG_T1 + 2)
dig_T3 = read_s16(REG_DIG_T1 + 4)

# Configure sensor: oversampling x1, normal mode
write_reg(REG_CTRL_MEAS, 0x27)

def read_temperature():
    data = read_reg(REG_TEMP, 3)
    raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    # Compensation formula from datasheet
    var1 = (((raw >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
    var2 = (((((raw >> 4) - dig_T1) * ((raw >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
    t_fine = var1 + var2
    T = (t_fine * 5 + 128) >> 8
    return T / 100.0

# Main loop
while True:
    temp = read_temperature()
    print("Temperature:", temp, "°C")
    time.sleep(1)
```



### C (Raspberry Pi Pico SDK, no external libs)

```c
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include <stdio.h>

#define BME280_ADDR 0x76

uint16_t read_u16(uint8_t reg) {
    uint8_t buf[2];
    i2c_write_blocking(i2c0, BME280_ADDR, &reg, 1, true);
    i2c_read_blocking(i2c0, BME280_ADDR, buf, 2, false);
    return buf[0] | (buf[1] << 8);
}

int16_t read_s16(uint8_t reg) {
    int16_t val = (int16_t)read_u16(reg);
    return val;
}
v
int main() {
    stdio_init_all();
    i2c_init(i2c0, 100 * 1000);
    gpio_set_function(4, GPIO_FUNC_I2C); // SDA
    gpio_set_function(5, GPIO_FUNC_I2C); // SCL
    gpio_pull_up(4);
    gpio_pull_up(5);

    // Read calibration
    uint16_t dig_T1 = read_u16(0x88);
    int16_t dig_T2 = read_s16(0x8A);
    int16_t dig_T3 = read_s16(0x8C);

    // Set ctrl_meas register: oversampling x1, normal mode
    uint8_t buf[2] = {0xF4, 0x27};
    i2c_write_blocking(i2c0, BME280_ADDR, buf, 2, false);

    while (1) {
        uint8_t reg = 0xFA;
        uint8_t data[3];
        i2c_write_blocking(i2c0, BME280_ADDR, &reg, 1, true);
        i2c_read_blocking(i2c0, BME280_ADDR, data, 3, false);

        int32_t raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);

        int32_t var1 = ((((raw >> 3) - ((int32_t)dig_T1 << 1))) * dig_T2) >> 11;
        int32_t var2 = (((((raw >> 4) - (int32_t)dig_T1) *
                          ((raw >> 4) - (int32_t)dig_T1)) >> 12) *
                        dig_T3) >> 14;

        int32_t t_fine = var1 + var2;
        int32_t T = (t_fine * 5 + 128) >> 8;

        printf("Temperature: %.2f C\n", T / 100.0);

        sleep_ms(1000);
    }
}
```


```
Raspberry Pi Pico (Top View, USB on Left)        BMP280 Breakout Board
+---------------------------+                   +------------------+
| [ ] 1   [ ] 2   [ ] 3 GND | ---- GND ---------| GND              |
| ...                       |  3.3v             | VIN -------------+
| [ ] 11 GP8  [ ] 12 ...    | ---- CS ----------| CS               |
| [ ] 14 GP10 [ ] 15 GP11   | ---- SCK ---------| SCK              |
| [ ] 16 GP12 [ ] 17 ...    | ---- SDO ---------| SDO (MISO)       |
| ...                       | ---- SDI ---------| SDI (MOSI)       |
| [ ] 36 3V3_OUT [ ] 37 ... |                   | 3Vo (NC)         |
| [ ] 38 GND [ ] 39 VSYS    |                   +------------------+
| [ ] 40 VBUS               |
+---------------------------+
```

Notes:
- VIN to Physical Pin 36 (3V3_OUT, 3.3V). Alt: Pin 40 (VBUS, 5V).
- GND to Physical Pin 3 (or any GND: 8, 13, 18, 23, 28, 33, 38).
- CS to Physical Pin 11 (GPIO 8, SPI1 CS).
- SCK to Physical Pin 14 (GPIO 10, SPI1 SCK).
- SDI (MOSI) to Physical Pin 15 (GPIO 11, SPI1 MOSI).
- SDO (MISO) to Physical Pin 16 (GPIO 12, SPI1 MISO).
- 3Vo: Not connected (NC).
- No pull-up resistors needed for SPI.
- Use a breadboard or soldered connections for stability.

