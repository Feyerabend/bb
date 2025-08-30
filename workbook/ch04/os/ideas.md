
OS ILLUSTRATION IDEA
scheduling, isolation, I/O, and interface — the key OS ideas in miniature

* A microkernel with message-passing + a simple shell.
* Processes = separate tasks (e.g., logging, display, sensor).
* Communication = messages (students see "no globals").
* Shell = user interacts with OS concepts.



Message-Passing Microkernel
- Principle: Isolation, IPC (inter-process communication).

- Define processes as tasks.
- They communicate only by sending messages (mailbox) through a central kernel "post office".
- Example: one process reads sensor, one logs to SD, one updates display.

- Very close to modern microkernel ideas.
- Stretch: Add message queues, priorities, or "drivers" as separate processes.




Interactive Shell
- Principle: User interface, command interpretation.

- One Pico runs a shell process on the display pack.
- Students type commands (via Wi-Fi "keyboard" from ordinary comp).
- Commands can be "apps" (processes) managed by the kernel.

- Shows interaction between kernel, filesystem, user space.
- Stretch: Add scripting, or combine with scheduler so commands run in background.


