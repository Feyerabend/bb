#define SYST_CSR    (*(volatile unsigned int*)0xE000E010)
#define SYST_RVR    (*(volatile unsigned int*)0xE000E014)
#define SYST_CVR    (*(volatile unsigned int*)0xE000E018)
#define GPIO_OUT    (*(volatile unsigned int*)0xD0000010)
#define GPIO_DIR    (*(volatile unsigned int*)0xD0000020)
#define LED_PIN     25

void delay(unsigned int ticks) {
    SYST_CVR = 0;              // Reset the timer counter
    SYST_RVR = ticks;          // Set reload value
    SYST_CSR = 5;              // Enable counter with no interrupt
    while ((SYST_CSR & (1 << 16)) == 0);  // Wait for the count flag
}

void main() {
    // Set LED_PIN as output
    GPIO_DIR |= (1 << LED_PIN);

    while (1) {
        GPIO_OUT ^= (1 << LED_PIN);  // Toggle LED
        delay(3000000);              // Delay for a while
    }
}