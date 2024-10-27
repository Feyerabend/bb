Adding a simple round-robin scheduler to your Raspberry Pi Pico operating system will allow you to create a form of multitasking, letting multiple “tasks” run in sequence by giving each task a time slice. This scheduler will not provide true parallelism but will allow the illusion of multiple tasks running simultaneously by quickly switching between them.

In this implementation, we’ll:

	1.	Set up a SysTick timer interrupt to act as our “scheduler tick.”
	2.	Maintain a list of task function pointers, and a current task index, and use the timer interrupt to switch to the next task in the list.

Here’s how you can create a simple round-robin scheduler from scratch.

1. Create Basic Task Management

Define a set of “tasks” as simple functions that will perform some operation or print output to UART. In our OS, each task can be a function that will get called when its turn comes up.

Each task will have a small Task Control Block (TCB) structure with its stack and program counter saved when switching tasks. For simplicity, we can assume that each task’s context is managed by its stack.

Task Control Block (TCB) Structure

Define a TCB structure with the following components:

	•	A stack pointer (to save/restore task state)
	•	The task function (to point to the function being run)

Here’s the definition:

```c
#define MAX_TASKS 4
#define STACK_SIZE 256

typedef struct {
    uint32_t *stack_pointer;
    void (*task_func)(void);
    uint32_t stack[STACK_SIZE];
} TaskControlBlock;

TaskControlBlock tasks[MAX_TASKS];
int current_task = 0;
int num_tasks = 0;
```

2. Task Creation

Define a function to create a new task. This function will set up a stack for each task, point to the task function, and configure the initial stack pointer.

```c
void create_task(void (*task_func)(void)) {
    if (num_tasks >= MAX_TASKS) return;

    // Initialize the Task Control Block for the new task
    TaskControlBlock *task = &tasks[num_tasks++];
    task->task_func = task_func;
    task->stack_pointer = &task->stack[STACK_SIZE - 16]; // Leave space for the initial register state

    // Set up the stack to simulate task function call
    task->stack[STACK_SIZE - 1] = 0x01000000;    // xPSR: Thumb state
    task->stack[STACK_SIZE - 2] = (uint32_t) task_func; // PC: start of task function
    task->stack[STACK_SIZE - 8] = 0xFFFFFFF9;    // LR: return using exception return
}
```

3. Context Switching with SysTick

Set up a SysTick timer interrupt to switch between tasks. The Cortex-M0+ doesn’t have a dedicated hardware context-switching mechanism, so we’ll handle it manually by saving and restoring the stack_pointer.

Here’s how you set up SysTick for periodic interrupts:

```c
#define SYSTICK_RELOAD_VALUE 3000000  // Define a reload value for a time slice

void systick_init() {
    SYST_RVR = SYSTICK_RELOAD_VALUE;  // Set reload value
    SYST_CVR = 0;                     // Clear current value register
    SYST_CSR = 7;                     // Enable SysTick with interrupts
}

void SysTick_Handler() {
    // Save the current task's stack pointer
    asm volatile("mrs %0, psp" : "=r"(tasks[current_task].stack_pointer));

    // Move to the next task in the round-robin
    current_task = (current_task + 1) % num_tasks;

    // Load the next task's stack pointer
    asm volatile("msr psp, %0" : : "r"(tasks[current_task].stack_pointer));
}
```

4. Implement the Scheduler in main

Initialize the SysTick timer and create a few example tasks.

```c
void task1() {
    while (1) {
        uart_send_string("Task 1 running...\n");
        for (volatile int i = 0; i < 100000; i++);  // Delay for demo
    }
}

void task2() {
    while (1) {
        uart_send_string("Task 2 running...\n");
        for (volatile int i = 0; i < 100000; i++);  // Delay for demo
    }
}

int main() {
    uart_init();
    systick_init();

    // Create tasks
    create_task(task1);
    create_task(task2);

    // Start first task
    current_task = 0;
    asm volatile("msr psp, %0" : : "r"(tasks[current_task].stack_pointer));
    asm volatile("svc 0");  // Start the first task by triggering an SVC exception

    while (1);  // Main loop does nothing
}
```

Explanation of Each Part

	1.	Task Creation (create_task):
	•	Initializes a stack for each task with initial register values (xPSR, PC) and simulates an initial call stack.
	2.	SysTick Initialization and Handler:
	•	systick_init sets up SysTick to fire periodically, which acts as the time slice for each task.
	•	SysTick_Handler saves the current task’s stack pointer, switches to the next task, and restores its stack pointer.
	3.	Main Function:
	•	Initializes UART, SysTick, and sets up tasks.
	•	Starts the first task by setting up the Process Stack Pointer (PSP) and triggers an SVC to begin the first task.

5. Compile and Run

Compile and flash as before to see task-switching in action. Each task should print a message indicating it’s running, and you’ll see these messages alternate based on the round-robin scheduler.

Summary

This basic round-robin scheduler gives each task a time slice using SysTick interrupts to trigger context switching. This setup lets each task run in sequence and demonstrates the fundamentals of multitasking, albeit in a simple form without preemption or priority handling.
