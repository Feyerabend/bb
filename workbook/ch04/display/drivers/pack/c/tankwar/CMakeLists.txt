cmake_minimum_required(VERSION 3.13)

# Include build functions from Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

# Set name of project (as PROJECT_NAME) and C/C++ Standards
project(cannon_defense C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the SDK
pico_sdk_init()

# Add executable. Default name is the project name, version 0.1
add_executable(cannon_defense 
    tankwar.c
    display.c
)

# Pull in our pico_stdlib which aggregates commonly used features
target_link_libraries(cannon_defense g
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_dma
    hardware_irq
    hardware_timer
    hardware_sync
    pico_time
)

# Enable usb output, disable uart output
pico_enable_stdio_usb(cannon_defense 1)
pico_enable_stdio_uart(cannon_defense 0)

# Create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(cannon_defense)

# Add url via pico_set_program_url
pico_set_program_name(cannon_defense "Cannon Defense Game")
pico_set_program_description(cannon_defense "Simple arcade cannon game for Pimoroni Display Pack 2.0")
pico_set_program_version(cannon_defense "0.1")
