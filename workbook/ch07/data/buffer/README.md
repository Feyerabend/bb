
## Buffers

#### A. [Double Buffer](./double/)
- Uses *two memory buffers*: one for reading, one for writing.
- Once writing completes, buffers *swap roles*.
- Prevents tearing or inconsistency, especially in *graphics
  rendering*, *audio streaming*, and *real-time processing*.
- Offers smooth transitions but may require synchronisation
  between producer and consumer.

#### B. [Gap Buffer](./gap/)
- Used mainly in *text editors* (e.g. Emacs).
- Maintains a *"gap"* in the middle of an array to allow fast
  insertions/deletions at the cursor.
- Buffer consists of `[text_before_gap][GAP][text_after_gap]`.
- Moving the cursor involves shifting the gap; editing is
  efficient if kept near the gap.
- Ideal for *frequent, localised text edits*.

#### C. [Circular Buffer](./circular/) (Ring Buffer)
- Fixed-size buffer with *wrap-around* behaviour.
- Uses head/tail pointers to track reads and writes.
- Common in *stream processing*, *audio*, *UART*, and
  *real-time systems*.
- Can block or reject writes when full unless used in
  *overwrite mode* (see overwrite ring buffer).
- Efficient and predictable memory usage.


### Other Buffers

#### 1. Overwrite Ring Buffer
- Variant of the circular buffer.
- When full, new data overwrites the *oldest data*.
- Suitable for logging or monitoring where only the
  most recent data matters.
- No blocking or overflow errors.

#### 2. Sliding Window Buffer
- Maintains a fixed-size "window" over a stream of data.
- Advances one unit (e.g., byte or packet) at a time.
- Common in *compression* algorithms (like LZ77) and
  *network protocols* (TCP receive windows).
- Useful for pattern recognition and temporal correlation.

#### 3. Block Buffer
- Buffers data in *fixed-size blocks* (e.g. 512 or 4096 bytes).
- Common in *file systems*, *disk I/O*, and *DMA transfers*.
- Optimises performance by reducing I/O calls.
- Often aligns with physical or OS-level block sizes.

#### 4. Audio Buffer
- Buffers real-time *audio samples* between producer and
  consumer (e.g. codec <-> speaker).
- Must ensure *low-latency* and *continuous flow* to prevent
  underruns or glitches.
- Size balances between latency and safety margin
  (e.g. 128–1024 samples).

#### 5. Pipe/Stream Buffer
- Used in *inter-process communication* (pipes, sockets)
  or *file I/O* streams.
- Temporarily holds data between producer and consumer.
- May be line-buffered (flush on newline) or block-buffered.
- Common in Unix `pipe` mechanisms and C `stdio`.

#### 6. Linear Buffer (Static Buffer)
- Fixed-size memory buffer, usually a plain array.
- Simple to manage, but size must be pre-determined.
- No dynamic allocation; useful in *embedded* or constrained environments.
- Risk of overflow unless carefully managed.

#### 7. Dynamic Buffer
- Buffer that *grows* as needed (e.g. using realloc).
- Common in text editing, serialisation, or flexible I/O systems.
- Allows efficient memory use for *variable-length data*.
- May require resizing/copying when full.
