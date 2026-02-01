cmake_minimum_required(VERSION 3.13)

# Include the Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(pico_program C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Pico SDK
pico_sdk_init()

# Add your executable
add_executable(pico_program
    pico_program.c
    display.c
)

# Link libraries
target_link_libraries(pico_program
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_dma
)

# Create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(pico_program)

# Enable USB output, disable UART output
pico_enable_stdio_usb(pico_program 1)
pico_enable_stdio_uart(pico_program 0)
