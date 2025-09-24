cmake_minimum_required(VERSION 3.13)

# Initialize the Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(mario_game C CXX ASM)

# Set C standard
set(CMAKE_C_STANDARD 11)

# Initialize the Pico SDK
pico_sdk_init()

# Create the executable
add_executable(mario_game
    mario.c
    display.c
)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(mario_game)

# Link libraries
target_link_libraries(mario_game
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_dma
    hardware_irq
    hardware_timer
    hardware_sync
)

# Enable USB output, disable UART output
pico_enable_stdio_usb(mario_game 1)
pico_enable_stdio_uart(mario_game 0)
