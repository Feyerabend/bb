Setting up UART on the Raspberry Pi Pico is a great way to output debug information and communicate with external devices. Since you’re working without external libraries, we’ll access the UART registers directly to configure and send data through UART.

Here’s how to set up UART for the Pico step-by-step.

1. Understanding the RP2040 UART Hardware

The RP2040 microcontroller has two UART peripherals: UART0 and UART1. By default, UART0 is mapped to GPIO0 (TX) and GPIO1 (RX), and these pins can be configured for different purposes using multiplexing.

To simplify, let’s focus on setting up UART0 with basic parameters:

	•	Baud Rate: Communication speed (e.g., 115200 baud).
	•	Data Format: 8 data bits, no parity, 1 stop bit (8N1).

2. Register Addresses for UART0

Here’s a summary of the key UART0 registers (you can find more details in the RP2040 datasheet):

	•	UART0_DR (Data Register) – Address: 0x40034000: Write to this register to send data.
	•	UART0_FR (Flag Register) – Address: 0x40034018: Holds flags indicating the UART’s status (e.g., if TX is busy).
	•	UART0_IBRD (Integer Baud Rate Divisor) – Address: 0x40034024: Sets the integer part of the baud rate divisor.
	•	UART0_FBRD (Fractional Baud Rate Divisor) – Address: 0x40034028: Sets the fractional part of the baud rate divisor.
	•	UART0_LCRH (Line Control Register) – Address: 0x4003402C: Configures data format (e.g., 8 bits, 1 stop bit, no parity).
	•	UART0_CR (Control Register) – Address: 0x40034030: Controls the enabling/disabling of UART.

3. Baud Rate Calculation

To set the baud rate, we need to configure IBRD and FBRD registers, based on the following formula:
￼
where UARTCLK for the RP2040 is typically 48 MHz.

For example, to set a baud rate of 115200:
￼

	•	The integer part (IBRD) is 26.
	•	The fractional part (FBRD) is calculated as:
￼

4. UART Initialization Code in C

Here’s the code to set up UART0 on the Pico for basic transmission:

```c
#define UART0_BASE      0x40034000
#define UART0_DR        (*(volatile unsigned int*)(UART0_BASE + 0x00))
#define UART0_FR        (*(volatile unsigned int*)(UART0_BASE + 0x18))
#define UART0_IBRD      (*(volatile unsigned int*)(UART0_BASE + 0x24))
#define UART0_FBRD      (*(volatile unsigned int*)(UART0_BASE + 0x28))
#define UART0_LCRH      (*(volatile unsigned int*)(UART0_BASE + 0x2C))
#define UART0_CR        (*(volatile unsigned int*)(UART0_BASE + 0x30))
#define UART0_IMSC      (*(volatile unsigned int*)(UART0_BASE + 0x38))

#define GPIO_BASE       0x40014000
#define GPIO_UART_TX    0
#define GPIO_UART_RX    1

void uart_init() {
    // Disable UART0 before configuring it
    UART0_CR = 0x0;
    
    // Set the integer & fractional part of the baud rate
    UART0_IBRD = 26;  // Integer part for 115200 baud rate
    UART0_FBRD = 3;   // Fractional part for 115200 baud rate
    
    // Set the UART line control for 8-bit, no parity, 1 stop bit (8N1)
    UART0_LCRH = (3 << 5);  // Set word length to 8 bits (WLEN field)

    // Enable UART0, TX, and RX
    UART0_CR = (1 << 9) | (1 << 8) | (1 << 0);
}

void uart_send_char(char c) {
    // Wait for UART0 to be ready to transmit (TXFF flag should be clear)
    while (UART0_FR & (1 << 5)) {
        // Spin until TX FIFO is not full
    }
    UART0_DR = c;  // Write character to data register
}

void uart_send_string(const char* str) {
    while (*str) {
        uart_send_char(*str++);
    }
}
```

Explanation of the Code

	1.	UART Initialization (uart_init):
	•	UART0_CR = 0x0: Disables UART0 temporarily to configure it.
	•	Sets the integer and fractional part of the baud rate (115200).
	•	Configures line control to 8 data bits, no parity, 1 stop bit (8N1).
	•	Enables UART0 and its TX and RX functions.
	2.	Sending Data (uart_send_char and uart_send_string):
	•	uart_send_char waits until the TX FIFO is not full (by checking the UART flag register UART0_FR) before sending a character.
	•	uart_send_string sends a null-terminated string one character at a time.

5. Setting Up GPIO for UART

Since GPIO pins are multiplexed on the Pico, configure GPIO0 and GPIO1 for UART functionality. You can do this by writing to the GPIO function select register (IO_BANK0), but to keep it simple, you can use the default UART pins GPIO0 and GPIO1 directly for TX and RX without additional GPIO setup.

6. Putting It All Together

Here’s an example program that initializes UART and sends a string:

```c
int main() {
    uart_init();  // Initialize UART

    uart_send_string("Hello, UART!\n");

    while (1) {
        uart_send_string("Sending data over UART...\n");
        for (volatile int i = 0; i < 1000000; i++);  // Simple delay
    }
    return 0;
}
```

7. Compile and Flash

Compile and flash this program as before, using the arm-none-eabi-gcc toolchain.

# Compile the main file with UART functions
arm-none-eabi-gcc -mcpu=cortex-m0 -mthumb -c main.c -o main.o

# Link the object file with the linker script
arm-none-eabi-ld -T pico.ld main.o -o main.elf

# Convert ELF to UF2 for Pico flashing
elf2uf2 main.elf main.uf2

Upload main.uf2 to the Pico’s USB storage, and the Pico should start sending data over UART0. To view this data, connect a USB-to-Serial adapter (or an oscilloscope if you’re testing) to the RX/TX pins on the Pico and open a serial terminal on your computer (e.g., PuTTY or screen on Linux).

Summary

This code sets up UART communication without external libraries by directly controlling registers. It gives you full control and a better understanding of how UART works at the hardware level. Once this setup works, you can expand it to support receiving data, adding interrupts, and implementing other communication protocols.
