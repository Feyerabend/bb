
__This repository__

* [intro](./intro/)               - Read some introduction to microcontrollers,
                                    the Raspberry Pi Pico and this repository

__Printed book reference: see explanations and examples in [BOOK].__

* [blink](./blink/)               - Simple samples of blinking LEDs in MicroPython and C
* [traffic](./traffic/)           - Traffic light simulations
* [temperature](./temperature/)   - Builtin sensor used as example for series of measurements  
* [db](./storage/db/)             - Connect to external SD card as secondary memory (database)
* [wire](./wire/)                 - Connect two Picos to each other for UART communication
* [mail](./wire/mail/)            - Connect two Picos with "mail" exchange


## Building and Experimenting

> [!NOTE]
> Code and samples refer to the original Raspberry Pi Pico (RP2040, dual-core Cortex-M0+,
> 133 MHz, 264 KB SRAM, 2 MB flash), unless specified otherwise.
> This is the currently the most affordable and easily accessible among the variations.
> You might have to modify code in case other alternatives are used, e.g. RPI Pico 2, or
> other boards with the RP2040 mounted.

> [!IMPORTANT]
> To seperate running C and Python (MicroPython to be exact) on the Raspberry Pi Pico,
> from that on your main computer (Windows, Macintosh or Linux, type), the repositories
> here are marked with names "c" or "micropython" for inteded use on the RPI Pico.
