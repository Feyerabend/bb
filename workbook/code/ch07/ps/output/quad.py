from PIL import Image, ImageDraw

def de_casteljau_quadratic(p0, p1, p2, t):
    # First interpolate between p0 and p1, and between p1 and p2
    q0 = ( (1 - t) * p0[0] + t * p1[0], (1 - t) * p0[1] + t * p1[1] )
    q1 = ( (1 - t) * p1[0] + t * p2[0], (1 - t) * p1[1] + t * p2[1] )
    
    # Then interpolate between q0 and q1 to get the final point on the curve
    p_t = ( (1 - t) * q0[0] + t * q1[0], (1 - t) * q0[1] + t * q1[1] )
    return p_t

def draw_quadratic_bezier(p0, p1, p2, image_size=(500, 500), steps=100):
    width, height = image_size
    # Create a white background image
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Draw control points
    for p in [p0, p1, p2]:
        draw.rectangle([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill="blue")

    # Draw the quadratic Bézier curve
    for i in range(steps):
        t = i / (steps - 1)
        pt = de_casteljau_quadratic(p0, p1, p2, t)
        if i == 0:
            prev_pt = pt
        draw.line([prev_pt, pt], fill="red", width=1)
        prev_pt = pt

    # Draw control polygon (lines between p0, p1, p2)
    draw.line([p0, p1, p2], fill="blue", width=1)
    
    # Save the image
    img.save("quadratic_bezier.png")
    img.show()

# Define the control points
p0 = (50, 400)
p1 = (250, 100)
p2 = (450, 400)

# Draw the quadratic Bézier curve
draw_quadratic_bezier(p0, p1, p2)