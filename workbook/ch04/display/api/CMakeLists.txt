cmake_minimum_required(VERSION 3.13)

# Include build functions from Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(display_pack_example C CXX ASM)

# Pico SDK init
pico_sdk_init()

# Add your source files
add_executable(display_pack_example
    example.c
    display_pack.c
)

# Pull in our pico_stdlib which aggregates commonly used features
target_link_libraries(display_pack_example
    pico_stdlib
    hardware_spi
    hardware_gpio
)

# Enable USB output, disable UART output
pico_enable_stdio_usb(display_pack_example 1)
pico_enable_stdio_uart(display_pack_example 0)

# Create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(display_pack_example)