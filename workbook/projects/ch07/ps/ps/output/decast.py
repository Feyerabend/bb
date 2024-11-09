import numpy as np
from PIL import Image, ImageDraw

# De Casteljau's Algorithm for cubic Bezier
def de_casteljau(t, p0, p1, p2, p3):
    # First step of De Casteljau's algorithm
    p01 = (1 - t) * p0 + t * p1
    p12 = (1 - t) * p1 + t * p2
    p23 = (1 - t) * p2 + t * p3
    
    # Second step
    p012 = (1 - t) * p01 + t * p12
    p123 = (1 - t) * p12 + t * p23
    
    # Final point on the curve
    p0123 = (1 - t) * p012 + t * p123
    
    return p0123

# Generate Bezier curve points using De Casteljau's algorithm
def generate_bezier_points(p0, p1, p2, p3, num_points=100):
    points = []
    for i in range(num_points + 1):
        t = i / num_points
        point = de_casteljau(t, p0, p1, p2, p3)
        points.append(tuple(np.round(point).astype(int)))  # Round to nearest pixel value
    return points

# Create a blank white image to draw the curve
def draw_bezier_curve(p0, p1, p2, p3, width=400, height=200, num_points=100):
    # Create an image with white background
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Generate points for the Bezier curve
    bezier_points = generate_bezier_points(p0, p1, p2, p3, num_points)

    # Draw the Bézier curve by connecting the points
    for i in range(1, len(bezier_points)):
        draw.line([bezier_points[i-1], bezier_points[i]], fill="blue", width=1)

    # Draw control points as red dots and lines connecting them
    control_points = [p0, p1, p2, p3]
    for i in range(len(control_points)):
        control_point = tuple(control_points[i])  # Convert to tuple if using NumPy arrays
        draw.ellipse((control_point[0] - 3, control_point[1] - 3,
                      control_point[0] + 3, control_point[1] + 3),
                     fill="red", outline="black")

    for i in range(len(control_points) - 1):
        control_point1 = tuple(control_points[i])
        control_point2 = tuple(control_points[i+1])
        draw.line([control_point1, control_point2], fill="red", width=1)

    # Return the image object
    return image

# Control points for the cubic Bezier curve
p0 = np.array([50, 150])
p1 = np.array([150, 50])
p2 = np.array([250, 50])
p3 = np.array([350, 150])

# Draw the curve and save it as PNG
image = draw_bezier_curve(p0, p1, p2, p3)

# Save the image to a file
output_path = "bezier_curve_pil.png"
image.save(output_path, format='PNG')

# Optionally, display the image
#image.show()