from PIL import Image, ImageDraw
import math

def draw_elliptical_arc(center, a, b, t1, t2, steps=100):
    # Create a blank image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # List to store points for the arc
    points = []
    
    # Parametric equation to calculate points along the ellipse
    for i in range(steps + 1):
        t = t1 + (t2 - t1) * i / steps  # Vary t from t1 to t2
        x = center[0] + a * math.cos(t)
        y = center[1] + b * math.sin(t)
        points.append((x, y))
    
    # Draw the points as an arc
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill='blue', width=2)

    # Save or show the image
    img.show()

# Define parameters for the elliptical arc
center = (400, 300)  # Center of the ellipse
a = 200  # Semi-major axis
b = 100  # Semi-minor axis
t1 = math.radians(0)  # Start angle (in radians)
t2 = math.radians(90)  # End angle (in radians)

# Draw the elliptical arc
draw_elliptical_arc(center, a, b, t1, t2)