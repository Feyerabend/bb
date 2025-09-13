cmake_minimum_required(VERSION 3.13)

# Import the pico-sdk
include(pico_sdk_import.cmake)

project(uart_communication C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the SDK
pico_sdk_init()

# Full duplex UART program (main device)
add_executable(full_duplex
    full_duplex.c
)

target_link_libraries(full_duplex 
    pico_stdlib 
    pico_multicore
    hardware_uart
    hardware_gpio
    hardware_adc
    pico_util
)

# Enable USB output and UART output
pico_enable_stdio_usb(full_duplex 1)
pico_enable_stdio_uart(full_duplex 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(full_duplex)

# Controller program
add_executable(controller
    controller.c
)

target_link_libraries(controller 
    pico_stdlib 
    pico_multicore
    hardware_uart
    hardware_gpio
    pico_util
)

# Enable USB output and UART output
pico_enable_stdio_usb(controller 1)
pico_enable_stdio_uart(controller 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(controller)