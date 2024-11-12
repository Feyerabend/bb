import math

def plot_line(x1, y1, x2, y2, thickness, image, color):
    """Draw a line with specified thickness."""
    # Bresenham's line algorithm
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    # Keep track of the points as we move along the line
    while True:
        # Draw the main point of the line
        if 0 <= int(x1) < len(image[0]) and 0 <= int(y1) < len(image):
            for i in range(-thickness // 2, thickness // 2 + 1):
                for j in range(-thickness // 2, thickness // 2 + 1):
                    ix = int(x1 + j)
                    iy = int(y1 + i)
                    if 0 <= ix < len(image[0]) and 0 <= iy < len(image):
                        image[iy][ix] = color

        # Check for termination (when we reach the final point)
        if x1 == x2 and y1 == y2:
            break

        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

# Function to calculate the shortened line's endpoint based on line thickness
def calculate_shortened_endpoint(x1, y1, x2, y2, thickness):
    """Shorten the endpoint of the line based on the line thickness."""
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)  # Find the angle of the line

    # Adjust the endpoint to shorten the line
    offset_x = math.cos(angle) * (thickness / 2)
    offset_y = math.sin(angle) * (thickness / 2)

    new_x2 = x2 - offset_x
    new_y2 = y2 - offset_y

    return new_x2, new_y2

# Function to draw the lines with calculated spacing and joins
def draw_separated_lines_with_joins(image, thickness, join_type='miter'):
    # Coordinates of the lines
    x1, y1 = 50, 50
    x2, y2 = 150, 50
    x3, y3 = 150, 150
    x4, y4 = 50, 150

    # Calculate offset for separation based on line thickness
    offset = thickness  # Separate by the thickness of the line

    # Shorten the first line
    x2, y2 = calculate_shortened_endpoint(x1, y1, x2, y2, thickness)

    # Draw the first line (red)
    plot_line(x1, y1, x2, y2, thickness, image, (255, 0, 0))

    # Shorten the second line and calculate its new endpoint
    x3, y3 = calculate_shortened_endpoint(x2, y2, x3, y3, thickness)

    # Draw the second line (blue), separated by the thickness
    plot_line(x2, y2, x3, y3, thickness, image, (0, 0, 255))

    # Shorten the third line and calculate its new endpoint
    x4, y4 = calculate_shortened_endpoint(x3, y3, x4, y4, thickness)

    # Draw the third line (green), separated by the thickness
    plot_line(x3, y3, x4, y4, thickness, image, (0, 255, 0))

    # Apply different joins (if needed)
    if join_type == 'miter':
        draw_miter_join(x2, y2, x3, y3, thickness, image)
    elif join_type == 'bevel':
        draw_bevel_join(x2, y2, x3, y3, thickness, image)
    elif join_type == 'round':
        draw_round_join(x2, y2, x3, y3, thickness, image)

# Functions for drawing different types of joins
def draw_miter_join(x2, y2, x3, y3, thickness, image):
    pass  # Implement miter join logic if needed

def draw_bevel_join(x2, y2, x3, y3, thickness, image):
    pass  # Implement bevel join logic if needed

def draw_round_join(x2, y2, x3, y3, thickness, image):
    pass  # Implement round join logic if needed

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

# Create an empty white image
width, height = 300, 300
image = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]

# Draw the separated lines with joins
draw_separated_lines_with_joins(image, thickness=10, join_type='miter')

# Save the resulting image as PPM
save_ppm(image, 'separated_lines_with_joins.ppm')