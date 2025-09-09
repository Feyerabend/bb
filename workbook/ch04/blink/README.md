
## Raspberry Pi Pico W Development Environment Setup

- A Raspberry Pi Pico/Pico W board
- A micro USB cable
- A computer running Windows, macOS, or Linux


### MicroPython Setup


#### 1. Install Thonny IDE
Thonny IDE provides a very convenient way for you to install it with one click, making
it the recommended editor for MicroPython development on the Pico/Pico W.

*Download and install Thonny:*
- Visit [thonny.org](https://thonny.org) and download the appropriate version for your
  operating system
- Install following the standard process for your OS


#### 2. Install MicroPython Firmware
*Method 1: Using Thonny (Recommended)*
1. Connect your Pico/Pico W while holding the BOOTSEL button
2. Release the BOOTSEL button after your Pico is mount as a Mass Storage Device called RPI-RP2
3. Open Thonny IDE
4. Go to Tools -> Options -> Interpreter
5. Select "MicroPython (Raspberry Pi Pico)" as the interpreter, or "MicroPython (Raspberry Pi Pico W)" as the interpreter
6. Click "Install or update MicroPython" and follow the prompts

*Method 2: Manual Installation*
1. Download the latest MicroPython UF2 file for
   Pico from [micropython.org](https://micropython.org/download/RPI_PICO/), or
   Pico W from [micropython.org](https://micropython.org/download/RPI_PICO_W/)
2. Hold BOOTSEL while connecting the Pico/Pico W to your computer
3. Drag and drop the UF2 file to the RPI-RP2 drive that appears
4. The Pico/Pico W will automatically reboot with MicroPython installed


#### 3. Verify Installation
- In Thonny, you should see the MicroPython REPL (command prompt) in the shell
- Try typing `print("Hello, Pico W!")` to test




### C/C++ SDK Setup

The C/C++ SDK provides more control and better performance but requires more setup.


#### 1. Install Required Tools

*Windows:*
- Download and install the official Pico SDK installer from the Raspberry Pi website
- This includes CMake, Build Tools for Visual Studio, Git, and the ARM GCC compiler
- Alternatively, install manually: Visual Studio Code, CMake, Git, and ARM GCC toolchain

*macOS:*
- Install Xcode command line tools: `xcode-select --install`
- Install CMake: `brew install cmake` (requires Homebrew)
- Install ARM GCC toolchain: `brew install --cask gcc-arm-embedded`

*Linux (Ubuntu/Debian):*
```bash
sudo apt update
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential git
```

#### 2. Download the Pico SDK
```bash
git clone https://github.com/raspberrypi/pico-sdk.git
cd pico-sdk
git submodule update --init
```

#### 3. Set Environment Variables
*Windows:* Add `PICO_SDK_PATH` pointing to your SDK directory
*macOS/Linux:* Add to your shell profile:
```bash
export PICO_SDK_PATH=/path/to/pico-sdk
```

#### 4. Install Visual Studio Code Extensions (Recommended)
- C/C++ Extension Pack
- CMake Tools
- Raspberry Pi Pico extension (provides project templates)

#### 5. Create Your First Project
1. Create a new directory for your project
2. Include the pico_sdk_import.cmake file and set up your CMakeLists.txt
3. Use the basic project template structure

#### 6. Building and Flashing
1. Create a build directory: `mkdir build && cd build`
2. Configure: `cmake ..`
3. Build: `make` (or `cmake --build .`)
4. Hold down the BOOTSEL on the Pico W as you plug it in, and it will show as an external drive
5. Copy the generated UF2 file to the RPI-RP2 drive



### Key Differences

*MicroPython:*
- Easier to get started
- Interactive development with REPL
- Slower execution but faster development
- Great for prototyping and learning
- Built-in WiFi libraries for Pico W

*C/C++:*
- Better performance and memory efficiency
- More complex setup
- Full access to hardware features
- Industry-standard for production embedded systems
- Requires compilation step


### Official Resources
- MicroPython is optimised to run on microcontrollers and in constrained environments
- Official Raspberry Pi documentation at raspberrypi.com/documentation/microcontrollers/
- Pico SDK on GitHub: github.com/raspberrypi/pico-sdk
- Getting Started PDF guide available from datasheets.raspberrypi.com

Both development paths are well-supported, and your choice depends on your project requirements,
performance needs, and personal preferences. MicroPython is excellent for beginners and rapid
prototyping, while C/C++ offers maximum control and performance for production applications.
