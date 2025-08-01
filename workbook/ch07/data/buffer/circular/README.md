
## Circular Buffers

A *circular buffer* (also called a *ring buffer*) is a fixed-size data structure
that treats its ends as connected—like a circle. It uses a single, fixed-size array
and two indices:

- *head*: the position to write new data
- *tail*: the position to read data from

When either index reaches the end of the buffer, it wraps around to the beginning.

Circular buffers are commonly used in embedded systems, audio/video streaming, and
producer–consumer scenarios, where memory usage must be predictable and efficient.

### Properties

- *Fixed memory footprint* – no dynamic allocation
- *Efficient operations* – constant-time read/write
- *Overwriting* or *overflow protection* – behaviour can be tailored:
  - *Overwrite old data* when full
  - *Block or signal error* when full

### Use

- UART/serial communication buffers
- Real-time audio or sensor sampling
- Inter-thread messaging queues

