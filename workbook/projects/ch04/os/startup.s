.section .text
.global _start

_start:
    ldr sp, =_stack_top    // Initialize stack pointer
    bl main                // Call the main function
    b .                     // Infinite loop if main returns
