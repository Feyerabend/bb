# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Initialise pico_sdk from installed location
# (note this can come from environment, CMake cache etc)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
cmake_minimum_required(VERSION 3.13)

# Include the Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(pico_particle C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Pico SDK
pico_sdk_init()

# Add display library
add_library(display STATIC
    display.c
)

target_link_libraries(display
    pico_stdlib
    hardware_spi
    hardware_dma
    hardware_gpio
    hardware_pwm
    hardware_irq
    hardware_sync
)

target_include_directories(display PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)

# Particle system executable
add_executable(particle
    main.c
)

target_link_libraries(particle
    pico_stdlib
    pico_multicore
    display
    hardware_sync
)

# Enable USB output, disable UART
pico_enable_stdio_usb(particle 1)
pico_enable_stdio_uart(particle 0)

# Create map/bin/hex/uf2 files
pico_add_extra_outputs(particle)

# Optional: Set the board type (for Pico 2 W)
# Uncomment if you have board definitions
# set(PICO_BOARD pico2_w)

