
## Custom Language to Raspberry Pi Pico 2 Compiler

This compiler translates a simple custom programming language into C
code that runs on the Raspberry Pi Pico 2 with display output.

- *Simple syntax* - let, if/else, while, print statements
- *Display output* - All output goes to an LCD display instead of console
- *Automatic type handling* - Supports both numbers and strings
- *No input required* - Perfect for embedded display applications
- *Two compilation targets*:
  - Virtual Machine (for testing)
  - Raspberry Pi Pico 2 (generates C code)


### Language Syntax

#### Variable Declaration
```
let x = 10;
let name = "Hello";
```

#### Assignment
```
x = x + 1;
```

#### Print Statement
```
print("Hello, World!");
print(x);
```

#### Conditionals
```
if x < 10 {
    print("Small");
} else {
    print("Large");
}
```

#### Loops
```
let i = 0;
while i < 10 {
    print(i);
    i = i + 1;
}
```

#### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`

### Usage

#### 1. Compile to Virtual Machine (Testing)
```bash
python3 compiler_pico.py program.txt --target vm --verbose
```

#### 2. Compile to Raspberry Pi Pico 2
```bash
python3 compiler_pico.py program.txt --target pico --output program.c
```

### Building for Raspberry Pi Pico 2

#### Prerequisites
1. Raspberry Pi Pico SDK installed
2. CMake and build tools
3. ARM GCC toolchain

#### Setup
1. Set the PICO_SDK_PATH environment variable:
```bash
export PICO_SDK_PATH=/path/to/pico-sdk
```

2. Create a project directory:
```bash
mkdir my_pico_project
cd my_pico_project
```

3. Copy the generated files:
```bash
cp pico_program.c .
cp display.c .
cp display.h .
cp CMakeLists.txt .
```

4. Build:
```bash
mkdir build
cd build
cmake ..
make
```

5. Flash to Pico:
   - Hold BOOTSEL button while connecting Pico to USB
   - Copy `pico_program.uf2` to the Pico drive


### Display Library

The generated code uses a display library that provides:
- `disp_init()` - Initialize the display
- `disp_clear(color)` - Clear screen
- `disp_draw_text(x, y, text, fg, bg)` - Draw text
- `disp_set_backlight(enabled)` - Control backlight

Text is automatically wrapped and scrolled when the display is full.


### Example Program

```
let message = "Pico Display Test";
print(message);

let x = 10;
let y = 20;

if x < y {
    print("x is less than y");
    let sum = x + y;
    print(sum);
}

let i = 0;
while i < 10 {
    print(i);
    i = i + 1;
}

print("Done!");
```


### Display Configuration

The generated code includes these constants that can be adjusted:
- `TEXT_LINE_HEIGHT` - Vertical spacing between lines (default: 10 pixels)
- `TEXT_START_X` - Left margin (default: 5 pixels)
- `TEXT_START_Y` - Top margin (default: 5 pixels)

Colors are defined in RGB565 format:
- `COLOR_BLACK`, `COLOR_WHITE`
- `COLOR_RED`, `COLOR_GREEN`, `COLOR_BLUE`
- `COLOR_YELLOW`, `COLOR_CYAN`, `COLOR_MAGENTA`


### Notes

- The `input()` statement is ignored on embedded systems (variables are initialized to 0)
- Strings are limited to 256 characters
- The display auto-scrolls when full
- Integer division uses floor division (`//`)
- All numeric variables are stored as `double` for simplicity


### Compiler Architecture

1. *Lexer* (`lexer.py`) - Tokenizes source code
2. **Parser* (`parser.py`) - Builds Abstract Syntax Tree
3. *Semantic Analyser* (`semantic.py`) - Checks for errors
4. *Code Generators*:
   - `codegen.py` - Generates bytecode for VM
   - `codegen_pico.py` - Generates C code for Pico
5. *Virtual Machine* (`vm.py`) - Executes bytecode (for testing)

