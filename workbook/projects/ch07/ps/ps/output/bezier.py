from PIL import Image

def plot(x, y, brightness, pixels):
    """Set the pixel with an intensity based on brightness (anti-aliasing)"""
    if 0 <= x < width and 0 <= y < height:
        # Convert brightness to grayscale intensity (0-255)
        intensity = int(255 * brightness)
        pixels[x, y] = (intensity, intensity, intensity)

def wu_line(x0, y0, x1, y1, pixels):
    """Wu's line algorithm to draw an anti-aliased line"""
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        # Swap x and y coordinates if the line is steep
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    # Ensure left-to-right drawing
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    # Calculate the gradients
    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1

    # Handle the first endpoint
    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = 1 - (x0 + 0.5 - int(x0 + 0.5))
    xpxl1 = xend
    ypxl1 = int(yend)
    
    if steep:
        plot(ypxl1, xpxl1, (1 - (yend - ypxl1)) * xgap, pixels)
        plot(ypxl1 + 1, xpxl1, (yend - ypxl1) * xgap, pixels)
    else:
        plot(xpxl1, ypxl1, (1 - (yend - ypxl1)) * xgap, pixels)
        plot(xpxl1, ypxl1 + 1, (yend - ypxl1) * xgap, pixels)

    # Main loop
    intery = yend + gradient  # First y-intersect for the main loop
    for x in range(xpxl1 + 1, int(x1)):
        y = int(intery)
        if steep:
            plot(y, x, 1 - (intery - y), pixels)
            plot(y + 1, x, intery - y, pixels)
        else:
            plot(x, y, 1 - (intery - y), pixels)
            plot(x, y + 1, intery - y, pixels)
        intery += gradient

    # Handle the last endpoint
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = x1 + 0.5 - int(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = int(yend)
    if steep:
        plot(ypxl2, xpxl2, (1 - (yend - ypxl2)) * xgap, pixels)
        plot(ypxl2 + 1, xpxl2, (yend - ypxl2) * xgap, pixels)
    else:
        plot(xpxl2, ypxl2, (1 - (yend - ypxl2)) * xgap, pixels)
        plot(xpxl2, ypxl2 + 1, (yend - ypxl2) * xgap, pixels)

def bezier(t, p0, p1, p2, p3):
    """Evaluate a cubic Bézier curve at parameter t"""
    x = ( (1 - t) ** 3 * p0[0] +
          3 * (1 - t) ** 2 * t * p1[0] +
          3 * (1 - t) * t ** 2 * p2[0] +
          t ** 3 * p3[0] )
    y = ( (1 - t) ** 3 * p0[1] +
          3 * (1 - t) ** 2 * t * p1[1] +
          3 * (1 - t) * t ** 2 * p2[1] +
          t ** 3 * p3[1] )
    return x, y

def draw_bezier(p0, p1, p2, p3, pixels, segments=100):
    """Draw a cubic Bézier curve with anti-aliasing using Wu's line algorithm"""
    for i in range(segments):
        t0 = i / segments
        t1 = (i + 1) / segments
        x0, y0 = bezier(t0, p0, p1, p2, p3)
        x1, y1 = bezier(t1, p0, p1, p2, p3)
        wu_line(x0, y0, x1, y1, pixels)

# Set up the image canvas
width, height = 200, 200
image = Image.new("RGB", (width, height), "white")
pixels = image.load()

# Control points for a cubic Bézier curve
p0 = (20, 180)
p1 = (50, 20)
p2 = (150, 20)
p3 = (180, 180)

# Draw the Bézier curve
draw_bezier(p0, p1, p2, p3, pixels)

# Save the output as PNG
image.save("antialiased_bezier_curve.png")