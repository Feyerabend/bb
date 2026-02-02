# Z80 Emulator Test Suite

A Z80 CPU emulator with a comprehensive test suite and build system.

## Project Structure

```
.
├── Makefile          - Build system and test runner
├── z80.h             - Z80 emulator header
├── z80.c             - Z80 emulator implementation
├── z80asm.py         - Z80 assembler (Python)
├── run_test.c        - Test runner program
└── tests/
    ├── hello.z80       - Hello World test
    ├── math.z80        - Arithmetic operations test
    ├── loop.z80        - Loop counter test
    ├── registers.z80   - Register operations test
    ├── stack.z80       - Stack operations test (PUSH/POP)
    └── subroutine.z80  - Subroutine test (CALL/RET)
```

## Quick Start

### Build Everything
```bash
make all
```

This compiles the C emulator and assembles all Z80 test programs.

### Run Tests

Run the default test:
```bash
make test
```

Run a specific test:
```bash
make test-hello
make test-math
make test-loop
make test-registers
make test-stack
make test-subroutine
```

Run all tests:
```bash
make test-all
```

## Build Targets

### Main Targets
- `make all` - Build emulator and assemble all test programs (default)
- `make run_test` - Build only the emulator executable
- `make hello.com` - Assemble specific Z80 program

### Test Targets
- `make test` - Run default test (hello)
- `make test-hello` - Hello World test
- `make test-math` - Arithmetic operations test
- `make test-loop` - Loop counter (0-9)
- `make test-registers` - Register operations
- `make test-stack` - Stack PUSH/POP operations
- `make test-subroutine` - Subroutine CALL/RET
- `make test-all` - Run all tests sequentially

### Utility Targets
- `make clean` - Remove compiled and assembled files
- `make clean-all` - Remove all generated files including backups
- `make rebuild` - Clean and rebuild everything
- `make debug` - Show Makefile variables
- `make help` - Show help message

## Test Programs

### hello.z80
Basic "Hello, World!" program that tests:
- String output via I/O ports
- Memory addressing
- Loop iteration
- Program termination

### math.z80
Arithmetic operations test:
- Variable storage in memory
- Addition operations
- ASCII conversion
- Result output

### loop.z80
Counter loop test (0-9):
- Counter variable management
- Comparison operations
- Loop control flow
- ASCII digit conversion

### registers.z80
Register operations test:
- 8-bit register loads
- 16-bit register pairs
- Register-to-register transfers
- String output

### stack.z80
Stack operations test:
- Stack pointer initialization
- PUSH operations
- POP operations
- Hex output formatting
- Verifies stack integrity

### subroutine.z80
Subroutine calls test:
- CALL instruction
- RET instruction
- Stack-based return addresses
- Multiple subroutine calls

## I/O Port Convention

The test programs use a simple I/O port convention:
- **Port 0**: Halt signal (terminates emulation)
- **Port 2**: Character output (prints to console)

## Memory Map

- `0x0000-0x00FF`: Reserved (contains halt instruction at 0x0000)
- `0x0100-0x7FFF`: Program code
- `0x8000-0xFFFF`: Variables and data

## Requirements

- GCC (C compiler)
- Python 3 (for assembler)
- GNU Make

## Compiler Flags

The Makefile uses these compiler settings:
- `-Wall -Wextra`: Enable comprehensive warnings
- `-std=c99`: Use C99 standard
- `-O2`: Optimization level 2

## Adding New Tests

1. Create a new `.z80` file in the project directory
2. Add the filename to `Z80_SOURCES` in the Makefile
3. Add a test target following the pattern:
   ```makefile
   test-mytest: mytest.com $(EXECUTABLE)
       @echo "=== Running mytest.z80 test ==="
       @ln -sf mytest.com test.com
       @./$(EXECUTABLE)
       @echo ""
   ```
4. Add the test to `test-all` target
5. Update the help text

## Troubleshooting

**"Failed to open test.com"**: Run `make all` first to build everything.

**Python assembler errors**: Ensure `z80asm.py` is executable and Python 3 is installed.

**Compilation errors**: Check that z80.c and z80.h are present and compatible with your compiler.

## License

This project is provided as-is for educational purposes.
