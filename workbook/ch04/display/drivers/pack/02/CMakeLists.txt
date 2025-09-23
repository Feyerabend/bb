cmake_minimum_required(VERSION 3.13)

# Include pico-sdk
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(main C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the SDK
pico_sdk_init()

# Add the executable
add_executable(main
    main.c
    engine.c
    display.c
)

# Include directories
target_include_directories(main PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link libraries
target_link_libraries(main 
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_dma
    hardware_irq
    hardware_timer
    hardware_sync
    pico_time
)

# Compiler optimizations for embedded
target_compile_options(main PRIVATE
    -O2                    # Optimize for speed
    -Wall                  # Enable warnings
    -Wextra               # Extra warnings
    -Wno-unused-parameter # Suppress unused parameter warnings
)

# Enable USB output, disable UART output
pico_enable_stdio_usb(main 1)
pico_enable_stdio_uart(main 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(main)

# Add memory usage information
target_link_options(main PRIVATE
    -Wl,--print-memory-usage
)