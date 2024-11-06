from PIL import Image

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

def draw_bezier_high_res(p0, p1, p2, p3, high_res_pixels, high_res_width, high_res_height, segments=1000):
    """Draw a cubic Bézier curve with supersampling at a high resolution"""
    for i in range(segments):
        t0 = i / segments
        t1 = (i + 1) / segments
        x0, y0 = bezier(t0, p0, p1, p2, p3)
        x1, y1 = bezier(t1, p0, p1, p2, p3)
        
        # Map the coordinates to the high-resolution image space
        x0 = int(x0 * high_res_width)
        y0 = int(y0 * high_res_height)
        x1 = int(x1 * high_res_width)
        y1 = int(y1 * high_res_height)
        
        # Draw a line between these points in high resolution
        wu_line(x0, y0, x1, y1, high_res_pixels, high_res_width, high_res_height)

def wu_line(x0, y0, x1, y1, pixels, width, height):
    """Wu's line algorithm to draw an anti-aliased line"""
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1

    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = 1 - (x0 + 0.5 - int(x0 + 0.5))
    xpxl1 = xend
    ypxl1 = int(yend)
    
    if steep:
        plot(ypxl1, xpxl1, (1 - (yend - ypxl1)) * xgap, pixels, width, height)
        plot(ypxl1 + 1, xpxl1, (yend - ypxl1) * xgap, pixels, width, height)
    else:
        plot(xpxl1, ypxl1, (1 - (yend - ypxl1)) * xgap, pixels, width, height)
        plot(xpxl1, ypxl1 + 1, (yend - ypxl1) * xgap, pixels, width, height)

    intery = yend + gradient
    for x in range(xpxl1 + 1, int(x1)):
        y = int(intery)
        if steep:
            plot(y, x, 1 - (intery - y), pixels, width, height)
            plot(y + 1, x, intery - y, pixels, width, height)
        else:
            plot(x, y, 1 - (intery - y), pixels, width, height)
            plot(x, y + 1, intery - y, pixels, width, height)
        intery += gradient

    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = x1 + 0.5 - int(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = int(yend)
    if steep:
        plot(ypxl2, xpxl2, (1 - (yend - ypxl2)) * xgap, pixels, width, height)
        plot(ypxl2 + 1, xpxl2, (yend - ypxl2) * xgap, pixels, width, height)
    else:
        plot(xpxl2, ypxl2, (1 - (yend - ypxl2)) * xgap, pixels, width, height)
        plot(xpxl2, ypxl2 + 1, (yend - ypxl2) * xgap, pixels, width, height)

def plot(x, y, brightness, pixels, width, height):
    """Set the pixel with an intensity based on brightness (anti-aliasing)"""
    if 0 <= x < width and 0 <= y < height:
        intensity = int(255 * brightness)
        pixels[x, y] = (intensity, intensity, intensity)

def downscale_image(high_res_image, width, height):
    """Downscale a high-resolution image to the target resolution using Lanczos resampling."""
    return high_res_image.resize((width, height), Image.Resampling.LANCZOS)

def normalize_points(points, x_min=0, x_max=1, y_min=0, y_max=1):
    """Normalize a list of 2D points to a given range [x_min, x_max] and [y_min, y_max]"""
    # Extract x and y coordinates from the list of points
    x_coords, y_coords = zip(*points)

    # Find the min and max values of the x and y coordinates
    x_range = (min(x_coords), max(x_coords))
    y_range = (min(y_coords), max(y_coords))

    # Normalize the points
    normalized_points = [
        (
            (x - x_range[0]) / (x_range[1] - x_range[0]) * (x_max - x_min) + x_min,
            (y - y_range[0]) / (y_range[1] - y_range[0]) * (y_max - y_min) + y_min
        )
        for x, y in points
    ]
    return normalized_points

# Set up the high-resolution image canvas
high_res_width, high_res_height = 800, 800
high_res_image = Image.new("RGB", (high_res_width, high_res_height), "white")
high_res_pixels = high_res_image.load()


# Example control points (non-normalized)
p0 = (50, 50)
p1 = (150, 200)
p2 = (350, 200)
p3 = (450, 50)

# Normalize these points to the range [0, 1]
normalized_points = normalize_points([p0, p1, p2, p3])

# Unpack the normalized points into individual variables
p0, p1, p2, p3 = normalized_points

draw_bezier_high_res(p0, p1, p2, p3, high_res_pixels, high_res_width, high_res_height)


# Control points for the Bézier curve
p0 = (0.1, 0.9)
p1 = (0.25, 0.1)
p2 = (0.75, 0.1)
p3 = (0.9, 0.9)

# Draw the Bézier curve in high resolution (supersampling)
draw_bezier_high_res(p0, p1, p2, p3, high_res_pixels, high_res_width, high_res_height)

# Downscale the image to the target resolution
width, height = 200, 200
final_image = downscale_image(high_res_image, width, height)

# Save the output as PNG
final_image.save("antialiased_bezier_curve_supersampled.png")