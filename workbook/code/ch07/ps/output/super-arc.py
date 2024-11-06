from PIL import Image, ImageDraw
import math

def draw_elliptical_arc_with_ssaa(center, a, b, t1, t2, width, height, super_sampling_factor=4, steps=100):
    # High resolution size
    high_res_width = width * super_sampling_factor
    high_res_height = height * super_sampling_factor
    
    # Create a high-resolution image (for anti-aliasing)
    high_res_img = Image.new('RGB', (high_res_width, high_res_height), 'white')
    high_res_draw = ImageDraw.Draw(high_res_img)
    
    # Parametric equation to calculate points along the ellipse
    high_res_points = []
    for i in range(steps + 1):
        t = t1 + (t2 - t1) * i / steps  # Vary t from t1 to t2
        x = center[0] + a * math.cos(t)
        y = center[1] + b * math.sin(t)
        
        # Scale points to high resolution
        high_res_points.append((x * super_sampling_factor, y * super_sampling_factor))
    
    # Draw the high resolution elliptical arc
    for i in range(len(high_res_points) - 1):
        high_res_draw.line([high_res_points[i], high_res_points[i + 1]], fill='blue', width=1)

    # Downscale to target resolution with anti-aliasing
    img = high_res_img.resize((width, height), Image.Resampling.LANCZOS)

    return img

# Define parameters for the elliptical arc
center = (400, 300)  # Center of the ellipse
a = 200  # Semi-major axis
b = 100  # Semi-minor axis
t1 = math.radians(0)  # Start angle (in radians)
t2 = math.radians(90)  # End angle (in radians)

# Image size
width, height = 800, 600

# Draw the elliptical arc with SSAA
result_img = draw_elliptical_arc_with_ssaa(center, a, b, t1, t2, width, height)

# Show the result
result_img.show()

# Optionally, save the result
# result_img.save("elliptical_arc_ssaa.png")