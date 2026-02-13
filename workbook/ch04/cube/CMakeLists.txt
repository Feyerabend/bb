# Pico SDK environment
# Make sure PICO_SDK_PATH is set in your environment
# Example: export PICO_SDK_PATH=/path/to/pico-sdk

cmake_minimum_required(VERSION 3.13)

# Common settings
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Include Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(pico_display_demos C CXX ASM)

# Initialize the SDK
pico_sdk_init()

# Common display library
add_library(display_lib STATIC
    display.c
)

target_link_libraries(display_lib
    pico_stdlib
    hardware_spi
    hardware_dma
    hardware_gpio
    hardware_irq
)

# 3D Cube
add_executable(cube3d
    main.c
)

target_link_libraries(cube3d
    display_lib
    pico_stdlib
    hardware_spi
    hardware_dma
)

pico_add_extra_outputs(cube3d)
pico_enable_stdio_usb(cube3d 1)
pico_enable_stdio_uart(cube3d 0)

# Enable warnings
target_compile_options(display_lib PRIVATE -Wall -Wextra)
target_compile_options(cube3d PRIVATE -Wall -Wextra)
