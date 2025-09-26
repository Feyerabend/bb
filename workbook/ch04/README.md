
__This repository__

* [intro](./intro/)               - Read some general introduction to microcontrollers,
                                    a bit on the Raspberry Pi Pico and this repository

__Printed book reference: see explanations and examples in [BOOK].__

* [blink](./blink/)               - Setup of development environment,
                                    simple samples of blinking LEDs in MicroPython and C
* [traffic](./traffic/)           - Traffic light simulations
* [temperature](./temperature/)   - Builtin sensor used as example for series of measurements  
* [db](./storage/db/)             - Connect to external SD card as secondary memory (database)
* [wire](./wire/)                 - Connect two wired Picos to each other for UART communication
* [mail](./wire/mail/)            - Connect two wired Picos with "mail" exchange
* ..
* [rsa](./secure/rsa/)            - RSA for encryption/decryption
* ..
* [practice](./practice/)         - Build your own computer


## Building and Experimenting

> [!NOTE]
> Code and samples refer to the original Raspberry Pi Pico (RP2040, dual-core Cortex-M0+, 133 MHz, 264 KB SRAM, 2 MB flash), unless specified otherwise. This is the currently the most affordable and easily accessible among the variations. You might have to modify code in case other alternatives are used, e.g. RPI Pico 2, or other boards with the RP2040 mounted.

> [!IMPORTANT]
> To distinguish between running C and Python (specifically MicroPython) on the Raspberry Pi Pico and programming on your main computer (whether Windows, macOS, or Linux), the repositories here are marked with either “c” or “micropython” to indicate their intended use on the Pico. Some areas, such as *device drivers*, are better handled in C, while topics like *wireless* communication are more easily demonstrated in MicroPython. As a result, not every concept is shown in both languages, and the language labels are applied selectively.



