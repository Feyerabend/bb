class GapBuffer:
    def __init__(self, size=64):
        self.buffer = [''] * size
        self.gap_start = 0
        self.gap_end = size

    def insert(self, char):
        if self.gap_start < self.gap_end:
            self.buffer[self.gap_start] = char
            self.gap_start += 1

    def delete(self):
        if self.gap_start > 0:
            self.gap_start -= 1

    def move_cursor_left(self):
        if self.gap_start > 0:
            self.gap_end -= 1
            self.buffer[self.gap_end] = self.buffer[self.gap_start - 1]
            self.gap_start -= 1

    def move_cursor_right(self):
        if self.gap_end < len(self.buffer):
            self.buffer[self.gap_start] = self.buffer[self.gap_end]
            self.gap_start += 1
            self.gap_end += 1

    def __str__(self):
        left = ''.join(self.buffer[:self.gap_start])
        gap = '_' * (self.gap_end - self.gap_start)
        right = ''.join(self.buffer[self.gap_end:])
        return f'"{left}[{gap}]{right}"'

# Example usage
gb = GapBuffer()

for c in "Hello":
    gb.insert(c)

print(gb)

gb.move_cursor_left()
gb.move_cursor_left()
gb.insert('_')

print(gb)

gb.delete()
print(gb)