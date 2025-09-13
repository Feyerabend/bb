cmake_minimum_required(VERSION 3.12)

# Pull in PICO SDK (must be before project)
include(pico_sdk_import.cmake)

# Pull in Pimoroni Pico libraries
include(pimoroni_pico_import.cmake)

project(pico_display_example C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the SDK
pico_sdk_init()

add_executable(${PROJECT_NAME}
    main.cpp
)

# Pull in our pico_stdlib which aggregates commonly used features
target_link_libraries(${PROJECT_NAME} 
    pico_stdlib
    pico_display_2        # Pimoroni Display Pack 2.0 library
    st7789               # ST7789 display driver
    pico_graphics        # Graphics library
)

# Enable USB output, disable UART output
pico_enable_stdio_usb(${PROJECT_NAME} 1)
pico_enable_stdio_uart(${PROJECT_NAME} 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(${PROJECT_NAME})