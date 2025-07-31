
## Double Buffering

*Double buffering* is a technique where two separate memory buffers are used to improve
performance and avoid data tearing or race conditions during read/write operations.

The idea is simple:

- One buffer is *active* (being read from or displayed).
- The other buffer is *inactive* (being written to or prepared).
- Once the write is complete, the buffers *swap roles*.

This ensures that the reader always sees a consistent and complete view, while the writer
can update data without interference.


### Use Cases

- *Graphics rendering*: prepare a full frame in the background before displaying it.
- *Audio streaming*: load one buffer while the other is playing.
- *Sensor data processing*: one thread fills a buffer while another processes the previous one.


### Benefits

- Avoids partial updates or inconsistent reads.
- Allows concurrent read/write (if synchronised correctly).
- Maintains predictable latency in real-time systems.


### Simplified Workflow

1. Initialise two buffers (`buffer0`, `buffer1`)
2. Set `active = buffer0`, `inactive = buffer1`
3. Loop:
   - Write new data to `inactive`
   - Swap `active` ↔ `inactive`
   - Use `active` for reading/displaying

*Optional: use flags or mutexes to coordinate access in multithreaded systems.*

