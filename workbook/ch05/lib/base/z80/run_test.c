#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "z80.h"

#define MEMORY_SIZE 0x10000
static uint8_t* memory = NULL;
static bool finished = 0;

static uint8_t rb(void* userdata, uint16_t addr) {
    (void)userdata;  // Unused - we use global memory pointer
    return memory[addr];
}

static void wb(void* userdata, uint16_t addr, uint8_t val) {
    (void)userdata;  // Unused - we use global memory pointer
    memory[addr] = val;
}

static uint8_t port_in(z80* const z, uint8_t port) {
    (void)z;     // Unused - simple implementation doesn't need CPU state
    (void)port;  // Unused - always return 0 for any port
    // Simple input - return 0
    return 0;
}

static void port_out(z80* const z, uint8_t port, uint8_t val) {
    (void)z;  // Unused - simple implementation doesn't need CPU state
    
    // Port 0 = halt signal
    if (port == 0) {
        finished = 1;
        return;
    }
    // Port 2 = print character
    if (port == 2) {
        printf("%c", val);
        fflush(stdout);
    }
}

int main(void) {
    memory = malloc(MEMORY_SIZE);
    if (!memory) {
        fprintf(stderr, "Failed to allocate memory\n");
        return 1;
    }
    memset(memory, 0, MEMORY_SIZE);
    
    // Load the program
    FILE* f = fopen("test.com", "rb");
    if (!f) {
        fprintf(stderr, "Failed to open test.com\n");
        free(memory);
        return 1;
    }
    
    fseek(f, 0, SEEK_END);
    size_t file_size = ftell(f);
    rewind(f);
    
    size_t loaded = fread(&memory[0x100], 1, file_size, f);
    fclose(f);
    
    printf("Loaded %zu bytes at 0x0100\n", loaded);
    printf("Starting execution...\n\n");
    printf("--- OUTPUT ---\n");
    
    // Initialize Z80
    z80 cpu;
    z80_init(&cpu);
    cpu.read_byte = rb;
    cpu.write_byte = wb;
    cpu.port_in = port_in;
    cpu.port_out = port_out;
    cpu.userdata = NULL;
    cpu.pc = 0x100;
    
    // Inject halt signal at address 0
    memory[0x0000] = 0xD3;  // out (n), a
    memory[0x0001] = 0x00;  // port 0
    
    // Run
    long steps = 0;
    while (!finished && steps < 100000) {
        z80_step(&cpu);
        steps++;
    }
    
    printf("\n--- END OUTPUT ---\n\n");
    printf("Executed %ld instructions\n", steps);
    printf("Final state:\n");
    printf("  PC: 0x%04X\n", cpu.pc);
    printf("  A:  0x%02X (%d)\n", cpu.a, cpu.a);
    printf("  BC: 0x%04X\n", (cpu.b << 8) | cpu.c);
    printf("  DE: 0x%04X\n", (cpu.d << 8) | cpu.e);
    printf("  HL: 0x%04X\n", (cpu.h << 8) | cpu.l);
    printf("  SP: 0x%04X\n", cpu.sp);
    
    // Show some memory contents (variables start at 0x8000)
    printf("\nMemory at 0x8000-0x800F (variables):\n  ");
    for (int i = 0; i < 16; i++) {
        printf("%02X ", memory[0x8000 + i]);
    }
    printf("\n");
    
    free(memory);
    return finished ? 0 : 1;
}

