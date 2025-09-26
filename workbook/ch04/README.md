
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
> To distinguish between running C and Python (specifically MicroPython) on the Raspberry Pi Pico and programming on your main computer (whether Windows, macOS, or Linux), the repositories here are marked with either "c" or "micropython" to indicate their intended use on the Pico. Some areas, such as *device drivers*, are better handled in C, while topics like *wireless* communication are more easily demonstrated in MicroPython. As a result, not every concept is shown in both languages, and the language labels are applied selectively. The aim is to explore how computers behave as systems, not just how they are wired.


The code in this folder is __not__ about electronics in the strict sense--we’re
not building circuits from scratch. Instead, the Raspberry Pi Pico is used as a
small, *practical model of a complete computer*. It has memory, I/O, communication,
timing, power, and error handling--all the same pieces larger systems have.


### Approaches to Hardware and Computing

In teaching and writing about computers, two broad traditions can be distinguished.

The first is the *electronics-oriented approach*, which begins with the physical
substrate of computation: circuits, transistors, logic gates, and the design of
processors at the register-transfer level. This path treats the computer as an
engineered artefact, emphasising measurement, precision, and the construction of
working devices. Code, when introduced, is seen largely as a way of exercising or
testing the underlying hardware.

The second is the *computational* or *systems-oriented approach*, where hardware
is used less as an end in itself and more as a lens for exploring the concepts of
computing. Here, a microcontroller such as the Raspberry Pi Pico serves as a small,
accessible model of a complete computer system. Rather than focusing on electronic
detail, the emphasis is on how the device illustrates key ideas: memory and storage,
input/output, communication, timing, concurrency, error handling, and resource
management.

The material collected here follows the second path. The Pico and its peripherals
are used as a concrete, practical anchor, but the real aim is to highlight general
principles of computing.

