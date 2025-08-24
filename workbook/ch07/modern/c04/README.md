
## Compiler with External Plugins

This version of `compiler.py`, along with the plugin files `complex_plugin.py` and
`optimal_plugin.py`, further enhances the PL/0-like compiler by introducing advanced
output organisation, new plugin-based analyses for code complexity and optimisation
opportunities, and improved integration of plugin results. Building on the second
version’s plugin architecture, nested block support, and TAC generation, this version
focuses on improving the output structure and adding sophisticated analysis plugins.


### Enhanced Compilation

The compilation process retains the core pipeline—lexing, parsing, plugin-based
processing, and output generation—but introduces significant improvements in
output management and analysis capabilities:

1. *Lexing and Parsing*: Unchanged from the second version, using `Lexer` with
   `MessageCollector` and `PackratParser` with support for `NestedBlockNode`.
2. *Plugin-Based Processing*: The `PluginRegistry` now supports new plugins from
   `complex_plugin.py` (complexity analysis, AST printing, optimisation hints,
   documentation) and `optimal_plugin.py` (optimisation analysis, peephole
   optimisation), enhancing code analysis.
3. *Output Organisation*: Outputs are now written to a dedicated directory
   (`<basename>_compilation/`), including C code, TAC, plugin-generated files
   (e.g., documentation, AST structure), and a summary file.
4. *New Analyses*: Plugins provide detailed metrics (e.g., cyclomatic complexity,
   optimisation opportunities) and generate reports for debugging and optimisation.


### Extended Components

#### 1. *Enhanced Output Organisation in `PL0Compiler.compile_file`*

The `compile_file` method now organises all outputs in a dedicated directory
named `<basename>_compilation/`, improving file management.

- *Key Features*:
  - Creates a directory based on the input filename (e.g., `program_compilation/` for `program.p`).
  - Writes outputs like C code (`program.c`), TAC (`program.tac`), and plugin-generated
    files (e.g., `program.md` for documentation) to this directory.
  - Copies the original source to `<basename>_source.p` for reference.
  - Generates a `summary.txt` file with compilation details, generated files, and plugin results.
  - Optionally writes the main C file to the specified `output_filename` for backward compatibility.
  - Example for `program.p`:
    ```
    program_compilation/
    ├── program.c
    ├── program.tac
    ├── program.md
    ├── program_ast.txt
    ├── program_optimizations.txt
    ├── program_source.p
    └── program_summary.txt
    ```
- *Improvement*: The second version wrote C and TAC files to the current directory,
  which could clutter the workspace. The new organised structure improves usability,
  especially for projects with multiple outputs.


#### 2. *ComplexityAnalyzerPlugin (`complex_plugin.py`)*

This plugin introduces code complexity analysis, calculating metrics like *cyclomatic
complexity*[^cyc], lines of code, and nesting depth.

- *Key Features*:
  - Uses a `ComplexityAnalyzer` visitor to traverse the AST.
  - *Cyclomatic Complexity*: Starts at 1, increments for each `if` or `while` node
    (control flow branches).
  - *Lines of Code*: Counts `AssignNode`, `CallNode`, `ReadNode`, and `WriteNode`
    as executable lines.
  - *Nesting Depth*: Tracks the maximum depth of nested `if`/`while` constructs.
  - *Number of Procedures*: Counts procedures in `BlockNode`.
  - Outputs metrics to `plugin_results` and logs via `messages.info`.
  - Example: For a program with one `if` and one `while`, complexity is 3.
- *Improvement*: The second version lacked complexity analysis. This plugin helps
  developers assess code maintainability and identify complex code that may need refactoring.

[^cyc]: Cyclomatic complexity is a software metric that measures the complexity of a program by counting the number of linearly independent paths through its control flow graph. Introduced by Thomas J. McCabe, it’s calculated as `M = E - N + 2P`, where E is the number of edges, N is the number of nodes, and P is the number of connected components in the graph. In practice, it’s often simplified to counting decision points (e.g., if, while, for) plus one for the program’s entry point. For example, a program with one if and one while statement has a complexity of 3. High cyclomatic complexity indicates more complex code, which may be harder to maintain or test, often suggesting refactoring to reduce risk of errors. In `compiler.py` the` ComplexityAnalyzerPlugin` computes this by incrementing a counter for each `if` or `while` node in the AST.


#### 3. *ASTPrinter Plugin (`complex_plugin.py`)*

The `ast_printer` function-based plugin generates a human-readable representation
of the AST, stored in `<basename>_ast.txt`.

- *Key Features*:
  - Uses an `ASTPrinter` visitor to traverse the AST, producing an indented string
    representation (e.g., `Block:`, `Assignment: x :=`, `Variable: x`).
  - Supports all node types, including `NestedBlockNode`.
  - Stores output in `context.generated_outputs["ast_structure"]`.
  - Example output for `var x; x := 5;`:
    ```
    Block:
      Variables: x
      Statement:
        Assignment: x :=
          Number: 5
    ```
- *Improvement*: The second version had no AST visualization. This plugin aids
  debugging and understanding of the program’s structure.


#### 4. *OptimizationHints Plugin (`complex_plugin.py`)*

The `optimization_hints` function-based plugin analyzes the code for optimisation
opportunities, leveraging results from `static_analysis` and `complexity_analyzer`.

- *Key Features*:
  - Identifies unused variables by comparing `declared_variables` and
    `used_variables` from `static_analysis`.
  - Flags high cyclomatic complexity (>10) and deep nesting (>3 levels)
    from `complexity_analyzer`.
  - Generates a report in `<basename>_optimizations.txt` with suggestions
    (e.g., “Unused variables detected: x, y”).
  - Stores results in `context.generated_outputs["optimization_hints"]` and metrics
    (e.g., `hints_count`) in `plugin_results`.
- *Improvement*: The second version lacked actionable optimization suggestions.
  This plugin guides developers toward improving code efficiency.


#### 5. *DocumentationGenerator Plugin (`complex_plugin.py`)*

The `documentation_generator` function-based plugin creates Markdown documentation
for the program, stored in `<basename>.md`.

- *Key Features*:
  - Uses `static_analysis` results to list variables and procedures.
  - Includes complexity metrics if `complexity_analyzer` ran.
  - Example output:
    ```markdown
    # PL/0 Program Documentation

    ## Variables
    - `x`: Integer variable

    ## Procedures
    - `proc()`: User-defined procedure

    ## Statistics
    - Variables declared: 1
    - Procedures defined: 1
    - Lines of code: 5
    - Cyclomatic complexity: 2
    - Maximum nesting depth: 1
    ```
- *Improvement*: The second version had no documentation generation. This
  plugin improves maintainability by providing a structured program overview.


#### 6. *OptimizationPlugin (`optimal_plugin.py`)*

The `OptimizationPlugin` analyzes the AST for optimisation opportunities like
constant folding, algebraic simplification, dead code elimination, and strength reduction.

- *Key Features*:
  - Uses an `OptimizationAnalyzer` visitor to identify:
    - *Constant Folding*: Operations like `5 + 3` that can be computed at compile time.
    - *Algebraic Simplification*: Operations like `x + 0`, `x * 1`, or `x * 0`.
    - *Dead Code*: `if` or `while` statements with constant conditions (e.g., `if 1 = 1`).
    - *Strength Reduction*: Operations like `x * 2` that can become `x + x`.
  - Generates a report in `<basename>_opt_analysis.txt` (e.g., “Constant folding opportunities: 2”).
  - Stores metrics in `plugin_results` (e.g., `{"constant_folding": 2, "algebraic_simplification": 1}`).
- *Improvement*: The second version referenced an `optimized_ast` but lacked actual optimisation
  analysis. This plugin identifies specific optimisation opportunities, though it doesn’t apply them!


#### 7. *PeepholeOptimizer Plugin (`optimal_plugin.py`)*

The `peephole_optimizer` function-based plugin identifies peephole optimisation patterns,
such as redundant assignments.

- *Key Features*:
  - Uses a `PeepholeAnalyzer` visitor to detect:
    - *Redundant Assignments*: Variables assigned multiple times without intervening use (e.g., `x := 1; x := 2;`).
    - *Unnecessary Operations*: Not fully implemented but reserved for patterns like redundant operations.
  - Tracks assignments per scope, resetting for procedure calls, `if`, or `while` nodes to account for control flow.
  - Generates a report in `<basename>_peephole.txt`.
- *Improvement*: The second version of the compiler had no peephole optimisation analysis. This plugin
  enhances optimisation by focusing on local patterns, complementing the broader `OptimizationPlugin`.


#### 8. *Summary File Generation*

The `compile_file` method generates a `<basename>_summary.txt` file with compilation details and plugin results.

- *Key Features*:
  - Includes input filename, compilation date, output directory, and list of generated files.
  - Summarizes plugin results (e.g., complexity metrics, optimization counts).
  - Example:
    ```
    PL/0 Compilation Summary for program.p
    ==================================================
    Input file: program.p
    Compilation date: 2025-08-24 08:34:00
    Output directory: program_compilation/

    Generated Files:
      • program.c - Compiled C code
      • program.tac - Three-Address Code
      • program.md - Documentation
      • program_ast.txt - Ast Structure
      • program_optimizations.txt - Optimization Hints
      • program_opt_analysis.txt - Optimization Analysis
      • program_peephole.txt - Peephole Analysis

    Plugin Analysis Results:
      • static_analysis:
        - declared_variables: ['x', 'y']
      • complexity_analyzer:
        - cyclomatic_complexity: 2
    ```
- *Improvement*: The second version only printed results to the console. The summary
  file provides a persistent, structured record of the compilation.


#### 9. *Visitor Pattern Enhancements*

The Visitor pattern is extended to support the new plugins’ visitors (`ComplexityAnalyzer`,
`ASTPrinter`, `OptimizationAnalyzer`, `PeepholeAnalyzer`).

- *New Visitor Methods*:
  - Each visitor implements `visit_*` methods for all AST nodes, focusing on their
    specific analysis (e.g., complexity, optimisation patterns).
  - `visit_nested_block` ensures proper handling of local scopes in nested blocks.
- *Improvement*: The second version’s Visitor pattern supported static analysis,
  TAC, and code generation. The new plugins expand its use for complexity analysis,
  AST visualization, and optimization detection.


### Example Workflow with New Features

For an input file `program.p`:
```
var x, y;
x := 5 + 3;
if 1 = 1 then y := x * 2;
end.
```

1. *Lexing and Parsing*: Produces an AST with a `BlockNode` containing `x`, `y`,
   an `AssignNode` (`x := 5 + 3`), and an `IfNode` with a constant condition.
2. *Plugin Execution*:
   - *Static Analysis*: Reports `x`, `y` as declared; warns if any are unused.
   - *Complexity Analysis*: Cyclomatic complexity = 2 (base + `if`); lines of
     code = 2; max nesting depth = 1.
   - *AST Printer*: Generates `program_ast.txt` with the AST structure.
   - *Optimisation Hints*: Suggests removing unused variables and refactoring
     if complexity is high.
   - *Documentation*: Creates `program.md` with variables, procedures, and stats.
   - *Optimisation Analysis*: Detects constant folding (`5 + 3`), strength
     reduction (`x * 2`), and dead code (`if 1 = 1`).
   - *Peephole Analysis*: Checks for redundant assignments.
   - *TAC and C Code*: Generates `program.tac` and `program.c`.
3. *Output*:
   - Directory `program_compilation/` contains:
     - `program.c`, `program.tac`, `program.md`, `program_ast.txt`,
       `program_optimizations.txt`, `program_opt_analysis.txt`,
       `program_peephole.txt`, `program_source.p`, `program_summary.txt`.
   - Console output lists all generated files and plugin results if `--debug` is enabled.


### Why Extend with These Features?

- *Organised Outputs*: The compilation directory and summary file improve usability
  by centralising and documenting outputs.
- *Complexity Analysis*: Helps developers identify complex code, improving maintainability.
- *Optimisation Insights*: The `OptimizationPlugin` and `PeepholeOptimizer` provide
  actionable suggestions, paving the way for actual optimisations.
- *Documentation and AST Visualization*: Enhances program understanding and debugging.
- *Extensibility*: The new plugins demonstrate how the plugin system supports diverse
  analyses without modifying the core compiler.


### Limitations and Potential Improvements

- *Optimisation Application*: The `OptimizationPlugin` identifies opportunities but
  doesn’t! apply them (no `optimized_ast` is generated). Adding an `Optimizer` visitor
  to transform the AST would complete this feature.
- *Peephole Limitations*: The `PeepholeAnalyzer` only detects redundant assignments;
  expanding to other patterns (e.g., redundant loads) would be valuable.
- *Plugin Dependencies*: Dependency management could be improved with version checking
  or conflict resolution.
- *Error Recovery*: The parser still halts on errors; adding recovery could improve
  usability.
- *Performance Metrics*: The summary could include compilation time or memory usage
  for profiling.


### Conclusion

The third version of `compiler.py`, with `complex_plugin.py` and `optimal_plugin.py`,
enhances the compiler by introducing organized output management, complexity analysis,
AST visualisation, optimisation suggestions, and documentation generation.
These features make the compiler more developer-friendly and suitable for real-world use,
while the plugin system continues to ensure extensibility. The new plugins leverage
the Visitor pattern effectively, providing detailed insights into code quality and
optimisation potential, making this version a robust tool for both learning and practical
compiler development.

