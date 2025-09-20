cmake_minimum_required(VERSION 3.13)

# Include build functions from Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(display C CXX ASM)

# Pico SDK init
pico_sdk_init()

# Add your source files
add_executable(display
    example.c
    display_pack.c
)

# Pull in our pico_stdlib which aggregates commonly used features
target_link_libraries(display
    pico_stdlib # already included?
    hardware_spi
    hardware_gpio
    hardware_dma
    hardware_irq
    pico_multicore
    pico_cyw43_arch_lwip_poll
    lwip
)

target_sources(display PRIVATE multicore_graphics.c)

# Enable USB output, disable UART output
pico_enable_stdio_usb(display 1)
pico_enable_stdio_uart(display 0)

# Create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(display)
