from PIL import Image, ImageDraw
import math

# Function to add extra points along a side to simulate the "V" shape
def divide_side(x1, y1, x2, y2, segments):
    points = []
    # Add the starting point
    points.append((x1, y1))
    
    # Calculate the intermediate points along the side
    for i in range(1, segments):
        x = x1 + (x2 - x1) * i / segments
        y = y1 + (y2 - y1) * i / segments
        points.append((x, y))
    
    # Add the final point
    points.append((x2, y2))
    
    return points

# Function to simulate the "V" shape and create more fractal detail
def koch_snowflake(x1, y1, x2, y2, iterations, segments=4):
    points = divide_side(x1, y1, x2, y2, segments)
    
    # Initialize a list to store the new points for the fractal
    new_points = []
    
    for i in range(len(points) - 1):
        x_start, y_start = points[i]
        x_end, y_end = points[i + 1]
        
        # Calculate the "V" shape (the peak of the Koch curve)
        dx = (x_end - x_start) / 3
        dy = (y_end - y_start) / 3
        xA = x_start + dx
        yA = y_start + dy
        xB = x_start + 2 * dx
        yB = y_start + 2 * dy
        
        # Calculate the peak of the triangle
        x_peak = (xA + xB) / 2 - (math.sqrt(3) / 6) * (yB - yA)
        y_peak = (yA + yB) / 2 + (math.sqrt(3) / 6) * (xB - xA)
        
        # Add the new points to the list
        new_points.append((x_start, y_start))
        new_points.append((xA, yA))
        new_points.append((x_peak, y_peak))
        new_points.append((xB, yB))
    
    # Add the final point
    new_points.append((points[-1][0], points[-1][1]))
    
    return new_points

# Function to draw the Koch snowflake
def draw_snowflake(iterations, segments=4, image_size=(600, 600)):
    # Create a blank image with white background
    img = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(img)

    # Define the initial points of an equilateral triangle
    size = 300
    height = size * math.sqrt(3) / 2
    xCenter = image_size[0] / 2
    yCenter = image_size[1] / 2

    # Three vertices of the triangle
    p1 = (xCenter, yCenter - height / 2)
    p2 = (xCenter - size / 2, yCenter + height / 2)
    p3 = (xCenter + size / 2, yCenter + height / 2)

    # Initialize the list of points
    points = []
    
    # Divide each side of the triangle into smaller segments
    points += koch_snowflake(p1[0], p1[1], p2[0], p2[1], iterations, segments)
    points += koch_snowflake(p2[0], p2[1], p3[0], p3[1], iterations, segments)
    points += koch_snowflake(p3[0], p3[1], p1[0], p1[1], iterations, segments)
    
    # Plot the Koch snowflake by connecting the points
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        draw.line([x1, y1, x2, y2], fill="blue")

    # Show the image
    img.show()

# Get user input for the number of iterations
iterations = int(input("Enter the number of iterations (1-4): "))

# Draw the Koch snowflake with the specified number of iterations
draw_snowflake(iterations)