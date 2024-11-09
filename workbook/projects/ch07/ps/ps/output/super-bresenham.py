from PIL import Image

# Bresenham's line algorithm implementation
def bresenham_line(x0, y0, x1, y1):
    """Generates points for a line from (x0, y0) to (x1, y1)"""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))  # Add current point to list
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
            
    return points

# Set up the image canvas
width, height = 200, 200
image = Image.new("RGB", (width, height), "white")  # Create a blank white image
pixels = image.load()  # Load pixel data for editing

# Use Bresenham's algorithm to get line points and set each pixel to black
line_points = bresenham_line(20, 20, 180, 180)  # Diagonal line from (20, 20) to (180, 180)
for x, y in line_points:
    pixels[x, y] = (0, 0, 0)  # Set the pixel to black

# Save the output as PNG
image.save("bresenham_line_output.png")
