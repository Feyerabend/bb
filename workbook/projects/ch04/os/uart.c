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