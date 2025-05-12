
```
%% #{init: {'theme': 'base', 'themeVariables': { 'fontSize': '12px'}}}%%
flowchart TD
    %% Main Components
    subgraph Core[Core Interpreter]
        Lisp[[Lisp]] -->|manages| GlobalEnv[Global Environment]
        Lisp -->|uses| Parser[Parser/Tokenizer]
        Lisp -->|evaluates| Eval[Evaluation Logic]
        Lisp -->|creates| Procedures
        GlobalEnv -->|parent reference| ParentEnv[Parent Environment]
    end

    subgraph REPL[REPL System]
        LispREPL[[LispREPL]] -->|contains| Lisp
        LispREPL -->|handles| UserInput[User Input]
        LispREPL -->|manages| History[Command History]
    end

    subgraph Extensions[Vector Extensions]
        register_vector_rasterizer_commands -->|adds to| GlobalEnv
        GlobalEnv -->|contains| VectorCmds[Vector Commands]
    end

    %% Data Flow
    UserInput -->|sends to| LispREPL
    LispREPL -->|executes via| Lisp.run
    Lisp.run -->|parses with| Parser
    Lisp.run -->|evaluates with| Eval
    Eval -->|reads/writes| GlobalEnv
    Eval -->|creates| NewEnv[New Environment]
    NewEnv -->|inherits from| ParentEnv
    Eval -->|executes| Procedures
    Procedures -->|create| ClosureEnv[Closure Environment]

    %% Key Dependencies
    Procedures -->|captures| GlobalEnv
    ParentEnv -.->|chain| GlobalEnv
    ClosureEnv -->|scoped under| GlobalEnv
    VectorCmds -->|used during| Eval

    %% Annotations
    classDef node fill:#f9f,stroke:#333,stroke-width:2px;
    classDef cluster fill:#e8f4ff,stroke:#6699ff,stroke-width:2px;
    class Core,REPL,Extensions cluster;
```