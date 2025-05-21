
## Introduction to CSP

*Communicating Sequential Processes (CSP)* is a formal language for describing and analyzing concurrent systems.[^hoare]
Developed by Tony Hoare in the late 1970s, it provides a mathematical framework for understanding how independent
processes can interact with each other. Think of it as a blueprint language for building complex software systems
where multiple parts run at the same time and need to coordinate their actions.

[^hoare]: Hoare ..

Here are the core ideas behind CSP:

* *Processes:* In CSP, a system is modeled as a collection of independent processes. Each process performs a
  sequence of actions. These actions can be internal (like a calculation) or external (communicating with another process).

* *Communication:* Processes communicate exclusively through *channels*. A channel is a medium through which two processes
  can exchange information. This communication is *synchronous*, meaning both the sending and receiving process must be
  ready for the communication to occur. If one process is ready but the other isn't, the ready process waits (or "blocks")
  until the other is also ready. This synchronized exchange is called a *rendezvous*.

* *Actions:* The fundamental building blocks of a CSP process are *actions*. These include:
    * *Send (!):* A process sends a message on a channel.
    * *Receive (?):* A process receives a message on a channel.
    * *Tau ($\tau$):* An internal, unobservable action. This represents an action that happens within a process and doesn't
      involve communication with other processes.

* *Operators:* CSP provides a set of operators to combine basic actions and processes into more complex behaviors:
    * *Prefix (a $\rightarrow$ P):* An action `a` followed by a process `P`. `P` can only start after `a` has completed.
    * *Sequential Composition (P; Q):* Process `P` runs to completion, and then process `Q` starts.
    * *Choice (P $\Box$ Q or P $\sqcap$ Q):*
        * *External Choice ($\Box$):* The environment (or an external event) determines which of `P` or `Q` will execute.
        * *Internal Choice ($\sqcap$):* The process itself non-deterministically chooses to behave as `P` or `Q`.
    * *Parallel (P || Q):* Processes `P` and `Q` execute concurrently. If they share channels, communication on those
      channels must be synchronized.
    * *Interleaving (P ||| Q):* Processes `P` and `Q` execute concurrently without any shared channels, meaning their
      actions can be interleaved in any order.
    * *Recursion ($\mu$ X . P):* Allows for repeating behaviors, where `X` refers to the process `P` itself, enabling loops.

* *Trace Semantics:* CSP uses traces (sequences of observable actions) to describe the behavior of processes. This allows
  for formal reasoning about properties like deadlock (where processes are stuck waiting for each other indefinitely) and
  livelock (where processes are busy but make no progress).

CSP is widely used in areas like:

* *Design and Verification of Concurrent Systems:* It helps engineers rigorously define and prove properties about
  parallel and distributed software.
* *Network Protocols:* Modeling and analyzing how different components of a network interact.
* *Operating Systems:* Understanding the synchronization mechanisms between various parts of an OS.


## Sample

The provided Python code implements a basic interpreter for a subset of CSP, allowing
you to execute and observe the behavior of CSP processes.


 A diagram representing the structure of the `main_process` example. Wwe'll focus on the parallel
 composition and the nested structure of your processes.


```mermaid
graph TD
    %% Nodes
    A[producer]
    B[consumer]
    C[monitor]
    D[deadlocker]
    E[Parallel]:::parallel
    F[Parallel]:::parallel

    %% Subgraph grouping only
    subgraph Main_Process
        A
        B
        C
        D
        E
        F
    end

    %% Styles
    style A fill:#aaffaa,stroke:#333,stroke-width:2px
    style B fill:#aaffaa,stroke:#333,stroke-width:2px
    style C fill:#aaffaa,stroke:#333,stroke-width:2px
    style D fill:#aaffaa,stroke:#333,stroke-width:2px

    %% Connections outside subgraphs
    A --||-- E
    E --> B

    B --||-- F
    F --> C
    F --> D

    C --||-- D

    %% Class for parallel channels
    classDef parallel fill:#e0e0e0,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;
```

*Explanation of the Diagram:*

* *`Main Process` Subgraph:* Represents the overall `main_process`.

* *Nodes (A, B, C, D):* These represent the individual processes (`producer`, `consumer`, `monitor`, `deadlocker`).

* *`Parallel (channels)` Subgraphs:* These denote the `Parallel` CSP operator. The channels listed in the parentheses
  are the ones over which the contained processes must synchronize.
    * The outermost `Parallel (data_channel)` connects `producer` with the rest of the system.
    * The next `Parallel (data_channel, status_channel)` connects `consumer` with the `monitor` and `deadlocker`.
    * The innermost `Parallel (data_channel, status_channel)` explicitly groups `monitor` and `deadlocker`.
* *`--||--` Connection:* This is a custom visual representation I'm using to indicate a *parallel composition* with
  shared channels.
* *`E` and `F` Nodes:* These are intermediate "Parallel" nodes used to correctly structure the nested `Parallel`
  operations in the diagram, mimicking the hierarchy:
    * `main_process = Parallel(producer, Parallel(consumer, Parallel(monitor, deadlocker, {"data_channel", "status_channel"}), {"data_channel", "status_channel"}), {"data_channel"})`

This diagram illustrates the hierarchical structure of your parallel processes and which
channels are involved in their synchronization at each level.

