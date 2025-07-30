
## Gap Buffer

A *gap buffer* is a data structure commonly used in text editors to allow efficient insertions
and deletions near the cursor. It consists of a single array split into three regions: text before
the cursor (pre-gap), a reserved empty space (the gap), and text after the cursor (post-gap).
The key idea is to perform edits in the gap to avoid shifting large amounts of text.


### How It Works

- *Init State*: The buffer is initialised with some text and a gap at the cursor's position.
For example, if the text is "hello" and the cursor is after "he", the buffer might look like:
  ```
  [h, e, _, _, _, l, l, o]
  ```
  Here, `_` represents the gap (empty slots).

- *Insert Characters*: When a character is typed at the cursor, it fills the first empty slot
in the gap, and the gap's start moves forward. For example, inserting "y" after "he":

  ```
  [h, e, y, _, _, l, l, o]
  ```

- *Deleting Characters*: Deleting a character before the cursor moves the gap's start backward,
effectively "absorbing" the deleted character into the gap:

  ```
  [h, _, _, _, _, l, l, o]  (after deleting "e")
  ```

- *Moving the Cursor*: Moving the cursor requires shifting characters to adjust the gap's position.
For example, moving the cursor right involves moving a character from the post-gap text into the gap:
  ```
  [h, e, l, _, _, l, o]  (cursor moved right)
  ```

- *Gap Management*: If the gap fills up (e.g., after many insertions), the buffer reallocates or
shifts text to create a larger gap. Similarly, if the gap is too large, it can be resized to save space.


The structure is efficient for local edits: insertions and deletions near the cursor are O(1), though
cursor movement may be O(n) in the worst case. The gap adds memory overhead but benefits
cache performance due to the contiguous layout.

Its simplicity and performance make it well-suited for scenarios with frequent cursor-local edits,
such as interactive text editors or command-line interfaces. However, it scales poorly for large
texts with frequent edits at arbitrary positions. In such cases, alternative structures like ropes
or piece tables may be preferable.

Compared to arrays or strings, a gap buffer avoids the high cost of shifting characters. Unlike linked
lists, it retains good cache locality. Compared to ropes or piece tables, it is easier to implement
but less flexible for non-local edits.

Visually, you can think of the gap as a movable hole in the text. You can type or delete quickly at
the hole’s location, but moving the hole itself--i.e., moving the cursor--requires effort, since it may
involve copying characters to reposition the gap.


### Concept

- *Structure*: The gap buffer is a single array or string that holds the text, split into three
  logical parts:
  1. *Pre-gap text*: The characters before the cursor.
  2. *Gap*: A reserved empty space (usually an array of null or placeholder characters).
  3. *Post-gap text*: The characters after the cursor.
- *Purpose of the Gap*: The gap acts as a buffer where new characters can be inserted without
shifting the entire text. Similarly, deletions near the cursor are efficient because they only
adjust the gap's boundaries.

- *Efficiency*:
  - Insertions and deletions at the cursor are O(1) since they only update the gap boundaries.
  - Cursor movement is O(n) in the worst case because it may require shifting characters to
    reposition the gap.
  - Memory usage is slightly higher due to the gap, but this trade-off enables fast edits.
- *Trade-offs*:
  - Best for scenarios with frequent edits near the cursor (e.g., typing in a text editor).
  - Less efficient for random-access edits far from the cursor, as moving the gap can be costly.
  - Memory overhead from the gap can be a concern in low-memory environments.


### Pros

- *Simplicity*: The gap buffer is straightforward to implement compared to more complex structures
  like ropes or piece tables.
- *Performance*: Optimised for common text-editing operations (typing, backspacing).
- *Locality*: Since it uses a single contiguous array, it benefits from cache locality.


### Limits

- *Cursor Movement*: Moving the cursor across large texts can be slow due to the need to shift characters.
- *Scalability*: For very large texts or frequent non-cursor edits, other structures like ropes or piece
  tables may perform better.
- *Memory*: The gap size must be managed carefully to balance performance and memory usage.


### Use

- *Text Editors*: Used in editors like Emacs (historically) for efficient real-time text manipulation.
- *Interactive Applications*: Suitable for any application requiring frequent insertions/deletions at a
   specific point (e.g., command-line interfaces).


### Comparison to Alternatives

- *Array/String*: Simple but slow for insertions/deletions (O(n) due to shifting).
- *Linked List*: Fast for random insertions/deletions but poor cache locality and complex cursor management.
- *Rope*: Better for large texts and random edits but more complex to implement.
- *Piece Table*: Efficient for edit histories (e.g., undo/redo) but overkill for simple editors.
