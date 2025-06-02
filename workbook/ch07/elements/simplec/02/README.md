
## Dynamic Plugin in C (Linux dependent)

This example demonstrates a dynamic plugin system in C, and requires a Linux (or Unix-like) environment to run.
The program uses `dlfcn.h` functions (`dlopen`, `dlsym`, `dlclose`) to load shared libraries at runtime. Thes
are part of the POSIX standard, widely supported on Linux and Unix-like systems (e.g., Ubuntu, Fedora, etc.).
A core program loads and uses plugins at runtime without needing to recompile. The system is flexible, robust,
and mimics real-world applications like text processing or computation.

The project folder should look something like this:

```
     project_root/
     ├── core.c
     ├── plugin_interface.h
     ├── Makefile
     └── plugins/
         ├── wordcount_plugin.c
         └── add_plugin.c
```


__1. Shared Interface (plugin_interface.h)__

*Purpose:* Defines the contract between the core program and plugins so they can communicate consistently.

*Structures:*
- Job: A struct holding input for plugins:
- data: A string (e.g., "Hello world" or "5 10") to process.
- option: An integer flag (e.g., 0 for default, 1 for verbose output).
- id: A unique job ID for tracking.

*Plugin:* A struct defining plugin functions:
- name(): Returns the plugin's name (e.g., "wordcount").
- init(config): Initializes the plugin with a configuration (e.g., a log file path).
- execute(job, result, result_size): Processes a Job, stores output in result, and returns a status
  (0 for success, non-zero for failure).
- cleanup(): Frees resources when the plugin is unloaded.

Location: Stored in the project root for shared access by the core and plugins.

__2. Core Program (core.c)__

*Role:* Loads plugins dynamically, manages them, and runs commands.

*Steps:*
Loading Plugins:
- 1. Opens the plugins directory using opendir.
- 2. Scans for files ending in _plugin.so (shared object files).
- 3. Uses dlopen to load each plugin dynamically into memory.
- 4. Finds the init_plugin function in each plugin via dlsym, which returns a Plugin struct.
- 5. Calls init(config) to set up the plugin (e.g., with "log.txt" for logging).
- 6. Stores loaded plugins and their handles in a PluginEntry array for tracking.

*Running Commands:*
- Takes a plugin name (e.g., "wordcount"), a Job (e.g., data "Hello world this is a test"), and a result buffer.
- Searches for a plugin by name, then calls its execute function to process the job.
- Stores output in the result buffer and checks the status (0 means success).
- Prints results or errors (e.g., "Command 'xyz' not found").

*Cleanup:*
- Calls each plugin’s cleanup function to free resources.
- Uses dlclose to unload plugins from memory.

*Features:*
- Dynamic loading via dlfcn.h (standard C, no external libraries).
- Error handling for loading, initialization, and execution.
- Supports up to 100 plugins (defined by MAX_PLUGINS).


__3. Plugins__

Plugins are shared libraries (.so files) compiled separately and loaded at runtime. Each implements the Plugin interface.


__`wordcount_plugin.c`__

*Purpose:* Counts words in a string and logs activity.

How It Works:
- Initialisation (init): Opens a log file (from config, e.g., "log.txt")
  in append mode and resets a job counter.
- Execution (execute):
    1. Takes a Job (e.g., data: "Hello world this is a test", option: 1, id: 1).
    2. Counts words by detecting spaces, newlines, or tabs.
    3. If option is 1 (verbose), logs the job details (ID, input, word count) to the file.
    4. Increments a job counter to track total jobs processed.
    5. Writes result (e.g., "Word count: 5 (total jobs: 1)") to the buffer.
    6. Returns 0 for success, -1 for errors (e.g., no input data).

- Cleanup: Closes the log file and resets the counter.
- State: Maintains a file pointer and job count, showing plugins can hold state.



__`add_plugin.c`__

*Purpose:* Adds two numbers and tracks a running total.

How It Works:
- Initialisation (init): Resets a running total to 0.
- Execution (execute):
    1. Takes a Job (e.g., data: "5 10", option: 0, id: 2).
    2. Parses two integers from the data string using sscanf.
    3. Computes their sum (e.g., 5 + 10 = 15).
    4. Adds the sum to a running total.
    5. If option is 1 (verbose), outputs detailed result (e.g., "Sum of 5 + 10 = 15 (running total: 15)").
    6. Otherwise, outputs simple result (e.g., "Sum: 15").
    7. Returns 0 for success, -1 for errors (e.g., invalid format).

- Cleanup: Resets the running total.
- State: Tracks a running sum, demonstrating persistent state.



__4. Building and Running__

*Commands:*
- make: Builds the core program and plugins.
- make clean: Removes compiled files.

- Run: Execute ./core to load plugins, run sample jobs
  (wordcount on "Hello world this is a test", add on "5 10"), and see results.


### Summary

- Dynamic: Plugins load at runtime—no need to recompile core.c to add new functionality.
- Modular: New plugins (e.g., reverse string, validate email) can be added by implementing the Plugin interface.
- Realistic: Mimics real systems (e.g., text processors, calculators) with state, config, and error handling.
- No Dependencies: Uses only standard C libraries (stdio.h, stdlib.h, string.h, dirent.h, dlfcn.h).

Example Flow

1. core loads wordcount_plugin.so and add_plugin.so from plugins/.
2. Initialises plugins with "log.txt" as config.
3. Runs wordcount on a job: "Hello world this is a test" (verbose),
   outputs "Word count: 5 (total jobs: 1)", logs to file.
4. Runs add on a job: "5 10" (not verbose), outputs "Sum: 15".
5. Cleans up and exits.

This system is extensible: add a new plugin by creating a .c file, implementing the interface, and compiling it to .so.

