
# data for each character
data = {

    # lower case example
    'a': [
        ((0, 1), (0, 3)),  #
        ((1, 0), (5, 0)),  #
        ((0, 1), (0, 3)),  #
        ((1, 0), (5, 0)),  #
        ((4, 1), (4, 6)),  #
        ((1, 4), (4, 4)),  #
        ((1, 7), (3, 7)),  #
    ],

    # upper case
    'A': [((0, 0), (2.5, 10)), ((2.5, 10), (5, 0)), ((1, 5), (4, 5))],
    'B': [((0, 0), (0, 10)), ((0, 10), (3, 10)), ((3, 10), (4, 9)), ((4, 9), (4, 6)), 
          ((4, 6), (3, 5)), ((3, 5), (4, 4)), ((4, 4), (4, 1)), ((4, 1), (3, 0)), 
          ((3, 0), (0, 0)), ((0, 5), (3, 5))],
    'C': [((5, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 9)), ((0, 9), (1, 10)),
          ((1, 10), (5, 10))],
    'D': [((0, 0), (0, 10)), ((0, 10), (3, 10)), ((3, 10), (4, 9)), ((4, 9), (4, 1)),
          ((4, 1), (3, 0)), ((0, 0), (3, 0))],
    'E': [((5, 0), (0, 0)), ((0, 0), (0, 10)), ((0, 10), (5, 10)), ((0, 5), (3, 5))],
    'F': [((0, 0), (0, 10)), ((0, 10), (5, 10)), ((0, 5), (3, 5))],
    'G': [((5, 7), (5, 10)), ((5, 10), (1, 10)), ((1, 10), (0, 9)), ((0, 9), (0, 1)),
          ((0, 1), (1, 0)), ((1, 0), (5, 0)), ((5, 0), (5, 4)), ((3, 4), (5, 4))],
    'H': [((0, 0), (0, 10)), ((5, 0), (5, 10)), ((0, 5), (5, 5))],
    'I': [((2, 0), (2, 10)), ((0, 0), (4, 0)), ((0, 10), (4, 10))],
    'J': [((5, 10), (5, 1)), ((5, 1), (4, 0)), ((4, 0), (1, 0)), ((1, 0), (0, 1))],
    'K': [((0, 0), (0, 10)), ((5, 10), (0, 5)), ((0, 5), (5, 0))],
    'L': [((0, 10), (0, 0)), ((0, 0), (5, 0))],
    'M': [((0, 0), (0, 10)), ((0, 10), (2.5, 5)), ((2.5, 5), (5, 10)), ((5, 10), (5, 0))],
    'N': [((0, 0), (0, 10)), ((0, 10), (5, 0)), ((5, 0), (5, 10))],
    'O': [((0, 0), (5, 0)), ((5, 0), (5, 10)), ((5, 10), (0, 10)), ((0, 10), (0, 0))],
    'P': [((0, 0), (0, 10)), ((0, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 6)),
          ((5, 6), (4, 5)), ((4, 5), (0, 5))],
    'Q': [((0, 0), (5, 0)), ((5, 0), (5, 10)), ((5, 10), (0, 10)), ((0, 10), (0, 0)),
          ((3, 3), (5, 0))],
    'R': [((0, 0), (0, 10)), ((0, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 6)),
          ((5, 6), (4, 5)), ((4, 5), (0, 5)), ((0, 5), (5, 0))],
    'S': [((5, 10), (1, 10)), ((1, 10), (0, 9)), ((0, 9), (1, 5)), ((1, 5), (4, 5)), 
          ((4, 5), (5, 1)), ((5, 1), (4, 0)), ((4, 0), (0, 0))],
    'T': [((2.5, 0), (2.5, 10)), ((0, 10), (5, 10))],
    'U': [((0, 10), (0, 1)), ((0, 1), (1, 0)), ((1, 0), (4, 0)), ((4, 0), (5, 1)),
          ((5, 1), (5, 10))],
    'V': [((0, 10), (2.5, 0)), ((2.5, 0), (5, 10))],
    'W': [((0, 10), (1.5, 0)), ((1.5, 0), (2.5, 5)), ((2.5, 5), (3.5, 0)), ((3.5, 0), (5, 10))],
    'X': [((0, 10), (5, 0)), ((5, 10), (0, 0))],
    'Y': [((0, 10), (2.5, 5)), ((2.5, 5), (5, 10)), ((2.5, 5), (2.5, 0))],
    'Z': [((0, 10), (5, 10)), ((5, 10), (0, 0)), ((0, 0), (5, 0))],

    # punctuation
    '.': [((1, 0), (1, 1))],
    ',': [((1, 0), (1, 1)), ((1, 0), (0.5, -0.5))],
    '!': [((1, 0), (1, 7)), ((1, 9), (1, 10))],
    '?': [((1, 7), (2.5, 10)), ((2.5, 10), (5, 7)), ((5, 7), (4, 5)), ((4, 5), (2.5, 3)), ((2.5, 3), (2.5, 1))],
    ':': [((1, 2), (1, 3)), ((1, 7), (1, 8))],
    ';': [((1, 2), (1, 3)), ((1, 0), (1, 1)), ((1, 0), (0.5, -0.5))],

    # numbers
    '0': [((1, 0), (4, 0)), ((4, 0), (5, 1)), ((5, 1), (5, 9)), ((5, 9), (4, 10)),
          ((4, 10), (1, 10)), ((1, 10), (0, 9)), ((0, 9), (0, 1)), ((0, 1), (1, 0)),
          ((5, 10), (0, 0))],
    '1': [((2.5, 0), (2.5, 10))],
    '2': [((0, 9), (1, 10)), ((1, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 5)), 
          ((5, 5), (0, 0)), ((0, 0), (5, 0))],
    '3': [((0, 10), (5, 10)), ((5, 10), (3, 5)), ((3, 5), (5, 0)), ((0, 0), (5, 0))],
    '4': [((4, 10), (4, 0)), ((0, 5), (5, 5)), ((4, 10), (0, 5))],
    '5': [((5, 10), (0, 10)), ((0, 10), (0, 5)), ((0, 5), (4, 5)), ((4, 5), (5, 4)),
          ((5, 4), (5, 0)), 
          ((5, 0), (0, 0))],
    '6': [((5, 10), (0, 10)), ((0, 10), (0, 0)), ((0, 0), (5, 0)), ((5, 0), (5, 4)), 
          ((5, 4), (4, 5)), ((4, 5), (0, 5))],
    '7': [((0, 10), (5, 10)), ((5, 10), (2, 0))],
    '8': [((1, 5), (4, 5)), ((1, 10), (4, 10)), ((4, 10), (5, 9)), ((5, 9), (5, 1)), 
          ((5, 1), (4, 0)), ((4, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 9)), 
          ((0, 9), (1, 10))],
    '9': [((5, 0), (5, 10)), ((5, 10), (0, 10)), ((0, 10), (0, 6)), ((0, 6), (1, 5)), 
          ((1, 5), (5, 5))]
}

# flags using bitwise shifts
NORMAL       = 1 << 0  # 1 (binary: 0001)
BOLD         = 1 << 1  # 2 (binary: 0010)
SLANTED      = 1 << 2  # 4 (binary: 0100)
SLANTEDBOLD  = 1 << 3  # 8 (binary: 1000)

# image and font settings
width, height = 240, 135    # Adjusted width for the whole alphabet
scale = 0.6               # Scale for the font size
margin = 12                # Margin around text
spacing = 7                # Spacing between characters

# empty image with white background
image = [[[255, 255, 255] for _ in range(width)] for _ in range(height)]

# slant angle factor for 15 degrees directly (approximately 0.26795)
shear_factor = 0.26795

# shearing function to apply to coordinates
def apply_shear(x, y):
    new_x = x + shear_factor * y
    return new_x, y

# draw a line on the image using Bresenham's algorithm
def draw_line(img, x1, y1, x2, y2, color=(0, 0, 0)):
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        if 0 <= x1 < len(img[0]) and 0 <= y1 < len(img):
            img[y1][x1] = color
        if (x1, y1) == (x2, y2):
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

# Function to render text with word wrapping and positioning on an image
def render_text_with_wrapping(words, img, start_x, start_y, letter_width=6, letter_height=14, line_width=100, spacing=2, style=NORMAL):
    x, y = start_x, start_y  # Initialize starting position at (start_x, start_y)

    for word in words:
        # Calculate the width of the word including spacing between letters
        word_width = len(word) * letter_width + (len(word) - 1) * spacing

        # Check if the word fits in the remaining space on the current line
        if x + word_width > start_x + line_width:
            # Move to the next line if the word doesn't fit
            x = start_x
            y += letter_height + spacing

        # Render each character in the word
        for char in word:
            if char in data:
                for line in data[char]:
                    (x1, y1), (x2, y2) = line

                    if style & (NORMAL | BOLD):
                        x1 = int(x + x1)
                        y1 = int(y - y1)
                        x2 = int(x + x2)
                        y2 = int(y - y2)
                        draw_line(img, x1, y1, x2, y2)

                        if style & BOLD:
                            draw_line(img, x1 + 1, y1, x2 + 1, y2)

                    elif style & (SLANTED | SLANTEDBOLD):
                        # Apply shear transformation for slanted styles
                        sx1, sy1 = apply_shear(x1, y1)
                        sx2, sy2 = apply_shear(x2, y2)
                        x1 = int(x + sx1)
                        y1 = int(y - sy1)
                        x2 = int(x + sx2)
                        y2 = int(y - sy2)
                        draw_line(img, x1, y1, x2, y2)
                    
                        if style & SLANTEDBOLD:
                            draw_line(img, x1 + 1, y1, x2 + 1, y2)

            # Move x to the right for the next character in the word
            x += letter_width + spacing

        # After finishing a word, add spacing to separate it from the next word
        x += letter_width + spacing # spacing

# Example usage
words = ["THE", "QUICK", "BROWN", "FOX", "JUMPS", "OVER", "THE", "LaZY", "DOG."]
render_text_with_wrapping(words, image, start_x=10, start_y=20, line_width=220, style=SLANTED)

# draw text on the image
#render_text("THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG", image, margin, height // 2, BOLD)
#render_text("0 1 2 3 4 5 6 7 8 9", image, margin, margin + spacing, SLANTED)
#render_text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", image, margin, margin, NORMAL)

# write PPM file
with open("picotext.ppm", "w") as f:
    f.write(f"P3\n{width} {height}\n255\n")
    for row in image:
        for pixel in row:
            f.write(f"{pixel[0]} {pixel[1]} {pixel[2]} ")
        f.write("\n")