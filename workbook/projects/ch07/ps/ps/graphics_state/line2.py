import math

def draw_line_thick_with_join(x1, y1, x2, y2, thickness, image, join_type="miter"):
    """
    Draws a thick line with the specified join type using Bresenham's algorithm.
    Supports three join types: 'miter', 'round', and 'bevel'.
    
    :param x1, y1: Start coordinates of the line
    :param x2, y2: End coordinates of the line
    :param thickness: Thickness of the line
    :param image: Image where the line is drawn (list of list for pixels)
    :param join_type: Type of join ('miter', 'round', or 'bevel')
    """
    def plot_line(x1, y1, x2, y2):
        """Bresenham's line algorithm to draw a line between two points"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            image[y1][x1] = (255, 0, 0)  # Red color for the line (as RGB)
            
            if x1 == x2 and y1 == y2:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
    
    # Draw the main line
    plot_line(x1, y1, x2, y2)
    
    # Helper function to draw a rounded or bevel join
    def draw_join(x1, y1, x2, y2, thickness, join_type):
        if join_type == "round":
            # Round join: Draw a small arc at the junction
            draw_round_join(x1, y1, x2, y2, thickness)
        elif join_type == "bevel":
            # Bevel join: Cut off the corner to form a flat edge
            draw_bevel_join(x1, y1, x2, y2, thickness)
        elif join_type == "miter":
            # Miter join: Extend the lines to meet at the sharp angle
            draw_miter_join(x1, y1, x2, y2, thickness)
    
    # Function to draw a round join
    def draw_round_join(x1, y1, x2, y2, thickness):
        # Drawing a circular arc at the junction of the two lines
        angle = math.atan2(y2 - y1, x2 - x1)
        radius = thickness / 2
        # Draw an arc (for simplicity, using small line segments)
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i * i + j * j <= radius * radius:
                    image[y1 + i][x1 + j] = (255, 0, 0)  # Red color for the join

    # Function to draw a bevel join
    def draw_bevel_join(x1, y1, x2, y2, thickness):
        # Drawing a flat bevel at the junction of the two lines
        # This simply connects the two lines by a straight line across the corner
        midpoint_x = (x1 + x2) // 2
        midpoint_y = (y1 + y2) // 2
        plot_line(x1, y1, midpoint_x, midpoint_y)
        plot_line(x2, y2, midpoint_x, midpoint_y)

    # Function to draw a miter join
    def draw_miter_join(x1, y1, x2, y2, thickness):
        # Miter join: Extend the outer edges of the lines until they meet
        dx1, dy1 = x2 - x1, y2 - y1
        dx2, dy2 = x1 - x2, y1 - y2
        angle = math.atan2(dy1, dx1)
        length = thickness * 2
        
        # Calculate the miter point, this is where the two lines intersect
        miter_x = int(x1 + length * math.cos(angle))
        miter_y = int(y1 + length * math.sin(angle))
        
        plot_line(miter_x, miter_y, x2, y2)

# Function to save the image as a PPM file
def save_ppm(image, filename):
    """Saves the image (a list of RGB tuples) as a PPM file."""
    height = len(image)
    width = len(image[0])
    
    # Open the file for writing
    with open(filename, 'w') as f:
        # PPM Header
        f.write(f'P3\n{width} {height}\n255\n')
        
        # Write pixel data
        for row in image:
            for pixel in row:
                f.write(f'{pixel[0]} {pixel[1]} {pixel[2]} ')
            f.write('\n')

# Example usage
width, height = 200, 200
# Create a blank image (a 2D list, where each pixel is an RGB tuple)
image = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]  # White background

# Draw a thick line with a bevel join
draw_line_thick_with_join(50, 50, 150, 50, 10, image, join_type="bevel")

# Save the image as PPM
save_ppm(image, 'output_with_bevel_join.ppm')
