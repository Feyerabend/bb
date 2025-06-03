
```
jvm_interpreter/
├── __init__.py
├── constants/
│   ├── __init__.py
│   └── jvm_constants.py
├── models/
│   ├── __init__.py
│   └── class_file_models.py
├── parser/
│   ├── __init__.py
│   └── class_file_parser.py
├── runtime/
│   ├── __init__.py
│   ├── class_loader.py
│   └── interpreter.py
├── utils/
│   ├── __init__.py
│   └── jvm_utils.py
└── api/
    ├── __init__.py
    └── jvm_api.py
main.py
```

## Java Virtual Machine-like Engine

- *jvm_interpreter/*: Root package for the project, making it importable as a library.
- *constants/*: Holds JVM-related constants (e.g., opcodes, tags, access flags).
- *models/*: Defines data models for class file components (e.g., Header, ClassFile).
- *parser/*: Contains parsing logic for reading and structuring .class files.
- *runtime/*: Manages runtime components like class loading and bytecode interpretation.
- *utils/*: Utility functions for formatting, decoding, and printing class file info.
- *api/*: Exposes a clean, high-level API for external use.
- *main.py*: Entry point for command-line execution, using the API.



### Hierarchical Structure

The code is organised into a *jvm_interpreter package* with submodules (*constants, models,
parser, runtime, utils, api*). Each submodule has a clear responsibility, improving maintainability
and readability.

Empty `__init__.py` files (except for the root) enable the package structure; the root `__init__.py`
exposes the main API class.


### Modularity

- *Constants*: JVM-specific constants are isolated in `jvm_constants.py`.
- *Models*: Data structures (e.g., `ClassFile`, `Header`) are grouped in `class_file_models.py`.
- *Parser*: Parsing logic for `.class` files is in `class_file_parser.py`.
- *Runtime*: Runtime components (`ClassLoader`, `Interpreter`) are under `runtime/`.
- *Utils*: Helper functions for decoding and printing are in `jvm_utils.py`.
- *API*: A clean `JavaClassInterpreter` class in `jvm_interpreter/api/jvm_api.py` provides
  a public interface.



### API for External Use

The `JavaClassInterpreter` class in `jvm_interpreter/api/jvm_api.py` offers methods
like `load_and_parse_class`, `get_method_code`, `run_method`, and `print_class_details`.
This allows external code to use the library, e.g.:

```python
from jvm_interpreter import JavaClassInterpreter
interpreter = JavaClassInterpreter(["/path/to/classes"])
class_file = interpreter.load_and_parse_class("MyClass")
interpreter.print_class_details(class_file)
result = interpreter.run_method("MyClass", "main", verbose=True)
```



### Reusability

The package structure makes it importable as a library for other projects.
Clear separation of concerns allows individual components (e.g., `ClassLoader`,
`Interpreter`) to be reused or extended.


### Execution

The *main.py* script serves as a command-line entry point, using the `JavaClassInterpreter` API.

```shell
python3 main.py Sample ./classes -v
```
