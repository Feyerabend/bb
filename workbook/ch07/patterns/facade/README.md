
## Façade Pattern




```mermaid
graph TD
    A[Composite] --> B((Manages Groups))
    C[Factory] --> D((Creates Shapes))
    E[Interpreter] --> F((Executes Scripts))
    G[Strategy] --> H((Rendering))
    I[Facade] --> J((VM Interface))
    B --> I
    D --> I
    F --> I
    H --> I
```



VM structure as central interface

VM encapsulates all system components

Simplified API via `processScriptFile(`

```c
typedef struct {
    int width;
    int height;
    int*** image;
    GraphicComponent** components;
    ScriptAST* ast;
    // .. other fields
} VM;

bool processScriptFile(const char* filename, ...) {
    // coordinates parser, VM, and renderer
}
```







