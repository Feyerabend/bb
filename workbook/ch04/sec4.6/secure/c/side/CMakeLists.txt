cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(side_channel_demo C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_executable(side_channel_demo
    main.c
    display.c
)

target_link_libraries(side_channel_demo
    pico_stdlib
    hardware_gpio
    hardware_timer
    hardware_spi
    hardware_dma
)

pico_enable_stdio_usb(side_channel_demo 1)
pico_enable_stdio_uart(side_channel_demo 0)
pico_add_extra_outputs(side_channel_demo)
