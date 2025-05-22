
## Introduction to CSP

*Communicating Sequential Processes (CSP)* is a formal language for describing and analysing concurrent systems.[^hoare]
Developed by Tony Hoare in the late 1970s, it provides a mathematical framework for understanding how independent
processes can interact with each other. Think of it as a blueprint language for building complex software systems
where multiple parts run at the same time and need to coordinate their actions.

[^hoare]: Hoare, C. A. R. (1978). Communicating sequential processes. *Communications of the ACM*, 21(8), 666–677.
https://doi.org/10.1145/359576.359585. https://www.cs.cmu.edu/~crary/819-f09/Hoare78.pdf.

Here are the core ideas behind CSP:

* *Processes:* In CSP, a system is modelled as a collection of independent processes. Each process performs a
  sequence of actions. These actions can be internal (like a calculation) or external (communicating with another process).

* *Communication:* Processes communicate exclusively through *channels*. A channel is a medium through which two processes
  can exchange information. This communication is *synchronous*, meaning both the sending and receiving process must be
  ready for the communication to occur. If one process is ready but the other isn't, the ready process waits (or "blocks")
  until the other is also ready. This synchronised exchange is called a *rendezvous*.

* *Actions:* The fundamental building blocks of a CSP process are *actions*. These include:
    * *Send (!):* A process sends a message on a channel.
    * *Receive (?):* A process receives a message on a channel.
    * *Tau ($\tau$):* An internal, unobservable action. This represents an action that happens within a process and doesn't
      involve communication with other processes.

* *Operators:* CSP provides a set of operators to combine basic actions and processes into more complex behaviours:
    * *Prefix (a $\rightarrow$ P):* An action `a` followed by a process `P`. `P` can only start after `a` has completed.
    * *Sequential Composition (P; Q):* Process `P` runs to completion, and then process `Q` starts.
    * *Choice (P $\Box$ Q or P $\sqcap$ Q):*
        * *External Choice ($\Box$):* The environment (or an external event) determines which of `P` or `Q` will execute.
        * *Internal Choice ($\sqcap$):* The process itself non-deterministically chooses to behave as `P` or `Q`.
    * *Parallel (P || Q):* Processes `P` and `Q` execute concurrently. If they share channels, communication on those
      channels must be synchronised.
    * *Interleaving (P ||| Q):* Processes `P` and `Q` execute concurrently without any shared channels, meaning their
      actions can be interleaved in any order.
    * *Recursion ($\mu$ X . P):* Allows for repeating behaviours, where `X` refers to the process `P` itself, enabling loops.

* *Trace Semantics:* CSP uses traces (sequences of observable actions) to describe the behaviour of processes. This allows
  for formal reasoning about properties like deadlock (where processes are stuck waiting for each other indefinitely) and
  livelock (where processes are busy but make no progress).

CSP is widely used in areas like:

* *Design and Verification of Concurrent Systems:* It helps engineers rigorously define and prove properties about
  parallel and distributed software.
* *Network Protocols:* Modelling and analysing how different components of a network interact.
* *Operating Systems:* Understanding the synchronisation mechanisms between various parts of an OS.


### Core Implementation Overview

This is a *formal CSP interpreter* in Python that implements Hoare-style CSP semantics with these key features:

1. *Process Algebra Foundation*:
   - Implements core CSP operators: prefix (`→`), sequential (`;`), choice (`□`), external choice (`⊓`), parallel (`||`), and recursion
   - Supports guarded processes with conditions

2. *Channel Communication*:
   - Synchronous (rendezvous) message passing
   - Channels maintain queues of blocked senders/receivers
   - Strict 1:1 matching between sends and receives

3. *Advanced Features*:
   - Recursive process definitions
   - Deadlock detection via dependency graph analysis
   - Tau (τ) silent actions
   - Nondeterministic choice

4. *Debugging Support*:
   - Verbose execution logging
   - Step-by-step process execution tracing
   - Timeout and step limits

#### Example Program Components

The demo includes these representative processes:

1. *Producer*:
   ```python
   Rec("P", Seq(
       Prefix(Send("data_channel", {"id": 2, "value": "item"}), SKIP()),
       Seq(Prefix(Tau(), Var("P")), STOP())
   ))
   ```
   - Continuously sends structured data
   - Uses τ-action for pacing

2. *Consumer*:
   ```python
   Rec("C", Seq(
       Prefix(Receive("data_channel", "msg"), SKIP()),
       If(Eq("msg", {...}), STOP(), Var("C"))
   ))
   ```
   - Pattern-matches received messages
   - Terminates on specific message match

3. *Monitor*:
   ```python
   Rec("M", Choice(
       Prefix(Send("status_channel", "active"), Var("M")),
       ExtChoice(Prefix(Tau(), Var("M")), SKIP())
   ))
   ```
   - Demonstrates internal vs external choice
   - Non-deterministic behavior

4. *Deadlock Detector*:
   ```python
   Prefix(Receive("data_channel", "dummy"), STOP())
   ```
   - Shows blocked process detection

#### Execution Model

1. *Scheduler* manages parallel composition:
   - Tracks all active processes
   - Handles channel synchronisation
   - Detects deadlocks via cycle detection

2. *State Management*:
   - Shared variables environment
   - Dynamic channel creation
   - Process dependency tracking

3. *Safety Mechanisms*:
   - Maximum step limits
   - Execution timeouts
   - Verbose diagnostics

### Differentiators
- *Formal Semantics*: Closely mirrors theoretical CSP
- *Diagnostic Capabilities*: Goes beyond basic execution with deadlock detection
- *Python Integration*: Implements process calculus in an OOP style while preserving algebraic properties

This implementation can be useful for:
- Protocol verification
- Concurrency pattern experimentation
- Model checking foundations

