
## Gap Buffer

A gap buffer is a data structure commonly used in text editors to allow efficient insertions and deletions near the cursor. It consists of a single array split into three regions: text before the cursor (pre-gap), a reserved empty space (the gap), and text after the cursor (post-gap). The key idea is to perform edits in the gap to avoid shifting large amounts of text.

When inserting a character, it fills the next position in the gap, and the gap’s start moves forward. For example, inserting “y” after “he” in the buffer [h, e, _, _, _, l, l, o] results in [h, e, y, _, _, l, l, o]. Deletion near the cursor moves the gap boundary backward, such as [h, _, _, _, _, l, l, o] after deleting “e”.

Cursor movement involves shifting characters to reposition the gap. Moving the cursor to the right might change [h, _, _, _, _, l, l, o] to [h, e, l, _, _, l, o] by moving characters from post-gap into the gap. If the gap becomes full, the buffer can reallocate and enlarge it; if it’s too large, it may shrink to conserve memory.

The structure is efficient for local edits: insertions and deletions near the cursor are O(1), though cursor movement may be O(n) in the worst case. The gap adds memory overhead but benefits cache performance due to the contiguous layout.

Its simplicity and performance make it well-suited for scenarios with frequent cursor-local edits, such as interactive text editors or command-line interfaces. However, it scales poorly for large texts with frequent edits at arbitrary positions. In such cases, alternative structures like ropes or piece tables may be preferable.

Compared to arrays or strings, a gap buffer avoids the high cost of shifting characters. Unlike linked lists, it retains good cache locality. Compared to ropes or piece tables, it is easier to implement but less flexible for non-local edits.

Visually, you can think of the gap as a movable hole in the text. You can type or delete quickly at the hole’s location, but moving the hole itself—i.e., moving the cursor—requires effort, since it may involve copying characters to reposition the gap.

