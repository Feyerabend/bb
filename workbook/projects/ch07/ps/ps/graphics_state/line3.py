import math

def plot_line(x1, y1, x2, y2, thickness, image, color):
    """Bresenham's line algorithm to draw a line between two points with thickness."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        # Check if the point is within the image bounds before drawing
        if 0 <= x1 < len(image[0]) and 0 <= y1 < len(image):
            # Use the thickness by drawing the surrounding points
            for i in range(-thickness//2, thickness//2 + 1):
                for j in range(-thickness//2, thickness//2 + 1):
                    if 0 <= x1 + j < len(image[0]) and 0 <= y1 + i < len(image):
                        image[y1 + i][x1 + j] = color  # Draw pixel with the chosen color

        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def draw_line_thick_with_join(x1, y1, x2, y2, thickness, image, color, join_type):
    """Draws a thick line with the specified join type using Bresenham's algorithm."""
    plot_line(x1, y1, x2, y2, thickness, image, color)
    
    # Draw the corner join between lines
    if join_type == "round":
        draw_round_join(x1, y1, x2, y2, thickness, image, color)
    elif join_type == "bevel":
        draw_bevel_join(x1, y1, x2, y2, thickness, image, color)
    elif join_type == "miter":
        draw_miter_join(x1, y1, x2, y2, thickness, image, color)

def draw_round_join(x1, y1, x2, y2, thickness, image, color):
    """Draws a round join at the intersection of two lines."""
    # The corner is drawn as a circular arc to connect the lines
    angle = math.atan2(y2 - y1, x2 - x1)
    radius = thickness // 2
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if i * i + j * j <= radius * radius:
                # Plot the points within the circle radius
                if 0 <= x1 + j < len(image[0]) and 0 <= y1 + i < len(image):
                    image[y1 + i][x1 + j] = color

def draw_bevel_join(x1, y1, x2, y2, thickness, image, color):
    """Draws a bevel join where the corner is cut off flat."""
    # Simply connect the two lines by adding a flat angle between them
    midpoint_x = (x1 + x2) // 2
    midpoint_y = (y1 + y2) // 2
    plot_line(x1, y1, midpoint_x, midpoint_y, thickness, image, color)
    plot_line(x2, y2, midpoint_x, midpoint_y, thickness, image, color)

def draw_miter_join(x1, y1, x2, y2, thickness, image, color):
    """Draws a miter join where the two lines meet at a sharp angle."""
    dx1, dy1 = x2 - x1, y2 - y1
    dx2, dy2 = x1 - x2, y1 - y2
    angle = math.atan2(dy1, dx1)
    length = thickness * 2
    
    # Calculate miter point and draw
    miter_x = int(x1 + length * math.cos(angle))
    miter_y = int(y1 + length * math.sin(angle))
    
    plot_line(miter_x, miter_y, x2, y2, thickness, image, color)

def save_ppm(image, filename):
    """Save the image as a PPM file."""
    with open(filename, 'w') as f:
        f.write("P3\n")
        f.write(f"{len(image[0])} {len(image)}\n")
        f.write("255\n")
        for row in image:
            for col in row:
                f.write(f"{col[0]} {col[1]} {col[2]} ")
            f.write("\n")

# Example usage: draw lines with different joins, thicknesses, and colors
width, height = 300, 300
image = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]  # White background

# Draw a Miter Join line in Red
draw_line_thick_with_join(50, 50, 150, 50, 15, image, (255, 0, 0), join_type="miter")
draw_line_thick_with_join(50, 50, 50, 150, 15, image, (255, 0, 0), join_type="miter")

# Draw a Round Join line in Green
draw_line_thick_with_join(200, 50, 200, 150, 20, image, (0, 255, 0), join_type="round")
draw_line_thick_with_join(150, 150, 200, 150, 20, image, (0, 255, 0), join_type="round")

# Draw a Bevel Join line in Blue
draw_line_thick_with_join(50, 200, 150, 200, 25, image, (0, 0, 255), join_type="bevel")
draw_line_thick_with_join(50, 200, 50, 250, 25, image, (0, 0, 255), join_type="bevel")

# Save the resulting image as PPM
save_ppm(image, 'output_with_various_joins.ppm')
