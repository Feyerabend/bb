# BASIC Interpreter User's Guide

## Overview
This is a Python-based BASIC interpreter implementing a subset of classic BASIC (inspired by Microsoft and Commodore BASIC). It supports interactive programming, file execution, and core BASIC features like loops, string comparisons, and file I/O.

## Running the Interpreter
- *Requirements*: Python 3.x.
- *Interactive Mode*:
  ```bash
  python3 basic.py
  ```
  - Starts the interpreter with a `>` prompt.
  - Type commands or program lines (e.g., `10 PRINT "Hello"`).
  - Type `BYE` to exit.
- *File Mode*:
  ```bash
  python3 basic.py program.bas
  ```
  - Loads and runs `program.bas`.
  - If interrupted (`Ctrl+C`), enters interactive mode.
- *Interrupts*:
  - First `Ctrl+C`: Pauses the program, allowing `CONTINUE` or other commands.
  - Second `Ctrl+C`: Exits the interpreter.

## Program Structure
- *Lines*: Programs consist of numbered lines (e.g., `10 PRINT "Hello"`).
  - Line numbers must be positive integers.
  - Lines are stored in memory and executed in order with `RUN`.
- *Statements*: Each line can contain multiple statements separated by colons (`:`).
  - Example: `10 PRINT "Hello" : PRINT "World"`
- *Variables*:
  - Numeric: `A`, `X1` (stored as integers or floats).
  - String: `A$`, `NAME$` (end with `$`).
  - Cannot use reserved words (e.g., `PRINT`, `RND`) as variable names.

## Supported Commands
Commands can be entered interactively or as part of a program. Case-insensitive.

- *PRINT expr[;expr][;]*:
  - Outputs expressions (numbers, strings, variables).
  - Semicolon (`;`) glues items without spaces; trailing `;` suppresses newline.
  - Comma (`,`) tabs to fixed positions (8, 16, 24, 32).
  - `USING` format for numbers (e.g., `PRINT USING "#.##"; 3.14159` outputs `3.14`).
  - Example: `PRINT "Score:"; 42;` → `Score:42`
- *LET var = expr*:
  - Assigns a value to a variable (numeric or string).
  - `LET` is optional: `A = 42` or `LET A = 42`.
  - Example: `A$ = "Hello" : A = 3.14`
- *INPUT [prompt;] var*:
  - Reads input into a variable (numeric or string).
  - Optional prompt (string expression).
  - Example: `INPUT "Name"; N$` → Prompts `Name `, stores input in `N$`.
- *IF condition THEN statement [ELSE statement]*:
  - Executes `THEN` if condition is non-zero, else `ELSE` if present.
  - Supports string comparisons (`=`, `<>`, `<`, `>`, `<=`, `>=`).
  - `THEN`/`ELSE` can be a line number (jump) or statement.
  - Example: `IF A$ < "B" THEN PRINT "Less" : ELSE PRINT "More"`
- *GOTO line*:
  - Jumps to the specified line number.
  - Example: `GOTO 100`
- *GOSUB line / RETURN*:
  - Calls a subroutine at the line number; `RETURN` resumes at the next line.
  - Example: `GOSUB 200 : PRINT "Back" : END` with `200 PRINT "Sub" : RETURN`
- *FOR var = start TO limit [STEP step] / NEXT var*:
  - Loops from `start` to `limit` with optional `step` (default 1).
  - Supports positive and negative steps.
  - Example: `FOR I = 1 TO 3 : PRINT I : NEXT I` → `1`, `2`, `3`
- *WHILE condition / WEND*:
  - Loops while condition is non-zero.
  - Example: `WHILE X < 5 : PRINT X : X = X + 1 : WEND`
- *STOP*:
  - Pauses execution; resume with `CONTINUE`.
- *CONTINUE*:
  - Resumes a paused program (after `STOP` or `Ctrl+C`).
- *END*:
  - Stops execution (no effect on program state).
- *LIST [start[-end]]*:
  - Lists program lines in the range (default: all lines).
  - Example: `LIST 10-20`
- *SAVE "filename"*:
  - Saves the program to `filename.bas`.
  - Example: `SAVE "prog"`
- *LOAD "filename"*:
  - Loads `filename.bas`, replacing the current program.
  - Example: `LOAD "prog"`
- *DEL [start[-end]]*:
  - Deletes lines in the range (default: all lines).
  - Example: `DEL 10-20`
- *REN [start[,increment]]*:
  - Renumbers lines starting at `start` (default 10) with `increment` (default 10).
  - Updates `GOTO`, `GOSUB`, `IF THEN` references.
  - Example: `REN 100,20`
- *RUN [line]*:
  - Runs the program from the specified line (default: first line).
  - Example: `RUN 50`
- *BYE*:
  - Exits the interpreter.

## Expressions
- *Numeric*: Constants (`3.14`), variables (`X`), arithmetic (`A + B * 2`), comparisons (`X < 5`).
- *String*: Literals (`"Hello"`), variables (`A$`), comparisons (`A$ = "Test"`).
- *Functions*:
  - Math: `SIN(X)`, `COS(X)`, `TAN(X)`, `ATN(X)`, `ABS(X)`, `SQR(X)`, `LOG(X)`, `EXP(X)`, `INT(X)`.
  - Random: `RND` (0 to 1), `RND(seed)` (seeded random).
  - String: `LEFT$(S, N)`, `RIGHT$(S, N)`, `MID$(S, Start[, Len])`, `LEN(S)`, `STR$(X)`, `VAL(S)`, `CHR$(N)`, `ASC(S)`.
- *Comparisons*: `=`, `<>`, `<`, `>`, `<=`, `>=` (numeric and lexicographic string comparisons).
  - Returns `1` (true) or `0` (false).
  - Example: `A$ < "Z"` → `1` if `A$` is lexicographically less than `"Z"`.

## Key Features
- *Colon-Separated Statements*: Multiple statements per line (e.g., `10 A = 1 : PRINT A`).
- *String Comparisons*: Lexicographic comparisons in `IF` and expressions (e.g., `IF A$ < B$ THEN ...`).
- *FOR Loops*: Fixed to iterate correctly with positive/negative steps.
- *SAVE/LOAD*: Stores programs to `.bas` files; loads with line numbers preserved.
- *PRINT Semicolons*: Glues output tightly; trailing `;` suppresses newline.
- *STOP/CONTINUE*: Pauses and resumes execution.
- *Ctrl+C*: First pauses, second exits.
- *Reserved Words*: Prevents misuse of keywords (`RND`, `PRINT`) as variables.

## Limitations
- No mixed-type comparisons (e.g., `A$ < 42` raises an error).
- String comparisons are case-sensitive.
- No `BREAK` command for loops (use `GOTO` to exit).
- `SAVE`/`LOAD` don’t preserve runtime state (e.g., variable values).
- Limited error recovery (errors may halt statements on a line).

## Example Programs
1. *Simple Loop*:
   ```
   10 FOR I = 1 TO 3 : PRINT "Count:";I
   20 NEXT I
   RUN
   ```
   Output:
   ```
   Count:1
   Count:2
   Count:3
   ```

2. *String Comparison*:
   ```
   10 A$ = "Apple" : B$ = "Banana"
   20 IF A$ < B$ THEN PRINT "Apple first" : GOTO 40
   30 PRINT "Banana first"
   40 END
   RUN
   ```
   Output:
   ```
   Apple first
   ```

3. *Interactive Input*:
   ```
   10 INPUT "Name"; N$
   20 PRINT "Hello, "; N$; "!"
   30 END
   RUN
   ```
   Output:
   ```
   Name? Alice
   Hello, Alice!
   ```

4. *Subroutine and Pause*:
   ```
   10 PRINT "Start" : GOSUB 100 : STOP
   20 PRINT "End"
   30 END
   100 PRINT "Subroutine" : RETURN
   RUN
   ```
   Output:
   ```
   Start
   Subroutine
   Program paused.
   > CONTINUE
   Resuming program...
   End
   ```

## Troubleshooting
- *Syntax Error*: Check command syntax (e.g., `IF` needs `THEN`).
- *No Matching NEXT/WEND*: Ensure `FOR`/`WHILE` loops are closed.
- *Program Paused*: Use `CONTINUE` to resume or `BYE` to exit.
- *File Not Found*: Verify `.bas` file exists for `LOAD`.
