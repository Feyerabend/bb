def draw_line_thick(x1, y1, x2, y2, thickness, image):
    """
    Draws a line with specified thickness using Bresenham's line algorithm
    and draws additional pixels for thickness around the main line.
    
    :param x1, y1: Start coordinates of the line
    :param x2, y2: End coordinates of the line
    :param thickness: Thickness of the line
    :param image: Image where the line is drawn (list of list for pixels)
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
    
    # Create a buffer for drawing thicker lines by adding pixels around the main line
    for d in range(1, thickness):
        # Add thickness by drawing lines perpendicular to the main line
        if x1 == x2:  # Vertical line
            plot_line(x1 + d, y1, x2 + d, y2)  # Right side
            plot_line(x1 - d, y1, x2 - d, y2)  # Left side
        elif y1 == y2:  # Horizontal line
            plot_line(x1, y1 + d, x2, y2 + d)  # Down side
            plot_line(x1, y1 - d, x2, y2 - d)  # Up side
        else:  # Diagonal lines (extend in both directions)
            plot_line(x1 + d, y1, x2 + d, y2)  # Right side
            plot_line(x1 - d, y1, x2 - d, y2)  # Left side
            plot_line(x1, y1 + d, x2, y2 + d)  # Down side
            plot_line(x1, y1 - d, x2, y2 - d)  # Up side

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

# Draw a line with a thickness of 5
draw_line_thick(50, 50, 150, 150, 5, image)

# Save the image as PPM
save_ppm(image, 'output.ppm')

print("Image saved as 'output.ppm'")
