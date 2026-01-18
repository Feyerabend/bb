cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(http_server_project C CXX ASM)
pico_sdk_init()

# Enable Pico W and lwIP
add_definitions(-DPICO_BOARD=pico_w)
add_definitions(-DLWIP=1)

# Add mbedtls (assuming subdirectory 'mbedtls')
add_subdirectory(mbedtls)
include_directories(mbedtls/include)

# Add cJSON for potential future use, but not needed here (assuming simple string)
add_subdirectory(cJSON)  # Optional; clone https://github.com/DaveGamble/cJSON
include_directories(cJSON)

add_executable(main
    main.c
)

target_link_libraries(main
    pico_stdlib
    pico_cyw43_arch_lwip_threadsafe_background
    pico_lwip_http
    tinyusb_device
    tinyusb_board
    mbedtls
    cjson  # Optional
)

pico_enable_stdio_usb(main 0)
pico_enable_stdio_uart(main 1)
pico_add_extra_outputs(main)