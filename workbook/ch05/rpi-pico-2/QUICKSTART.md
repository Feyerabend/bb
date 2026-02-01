
## Quick Start Guide - Pico Code Generator


### Quick Test (Virtual Machine)

```bash
## Test your program in the VM first
python3 compiler_pico.py sample_program.txt --target vm -v
```


### Generate C Code for Pico

```bash
## Generate C code
python3 compiler_pico.py sample_program.txt --target pico --output my_program.c

## Or use the demo
python3 compiler_pico.py demo_math.txt --target pico --output demo.c
```


### Files You Need for Pico Project

1. *Generated code*: `my_program.c` (or `pico_program.c`)
2. *Display library*: `display.h` and `display.c`
3. *Build config*: `CMakeLists.txt`


### Build Commands

```bash
## Set SDK path (once per session)
export PICO_SDK_PATH=/path/to/pico-sdk

## Create build directory
mkdir build && cd build

## Configure and build
cmake ..
make

## Result: pico_program.uf2
```


### Flash to Pico

1. Hold BOOTSEL button
2. Connect Pico via USB
3. Copy `pico_program.uf2` to the Pico drive
4. Pico reboots and runs your program


### Modify Display Settings

Edit the constants in the generated C file:

```c
#define TEXT_LINE_HEIGHT 10  // Line spacing
#define TEXT_START_X 5       // Left margin
#define TEXT_START_Y 5       // Top margin
```

Change colors in `display_print()`:
```c
disp_draw_text(TEXT_START_X, display_y, str, COLOR_GREEN, COLOR_BLACK);
```


### Language Cheat Sheet

```
## Variables
let x = 10;           ## Declare number
let name = "Alice";   ## Declare string
x = x + 1;            ## Assign

## Output
print("Hello!");      ## Print string
print(x);             ## Print number

## Conditionals
if x < 10 {
    print("Small");
} else {
    print("Big");
}

## Loops
while x < 100 {
    x = x * 2;
    print(x);
}
```

### Math
```
+ - * / %              ## Operators
==  !=  <  >  <=  >=   ## Comparisons
```

### Troubleshooting

*Semantic errors?*
- Make sure variables are declared with `let` before use
- Don't redeclare variables

*Build errors?*
- Check PICO_SDK_PATH is set
- Ensure all files (display.h, display.c, program.c) are in project

*Display not working?*
- Check your hardware connections
- Verify display initialization in display.c matches your hardware


### Examples Included

- `sample_program.txt` - Basic features demo
- `demo_math.txt` - Math quiz with Fibonacci sequence


### Next Steps

1. Write your own program in the custom language
2. Test with `--target vm`
3. Generate C code with `--target pico`
4. Build and flash to Pico
5. Enjoy your program on the display!
