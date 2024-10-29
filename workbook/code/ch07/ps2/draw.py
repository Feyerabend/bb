# draw.py

def draw_line(image, start, end, color):
    x0, y0 = start
    x1, y1 = end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        image[y0][x0] = color  # set pixel
        if (x0 == x1) and (y0 == y1):
            break
        err2 = err * 2
        if err2 > -dy:
            err -= dy
            x0 += sx
        if err2 < dx:
            err += dx
            y0 += sy

def draw_bezier_curve(image, p0, p1, p2, color):
    # calculate points on a quadratic Bezier curve
    for t in [i / 100.0 for i in range(101)]:  # 0 to 1 in 100 steps
        x = int((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0])
        y = int((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
        if 0 <= x < len(image[0]) and 0 <= y < len(image):  # ensure within bounds
            image[y][x] = color  # set pixel

def draw_cubic_bezier_curve(image, p0, p1, p2, p3, color):
    # Calculate points on a cubic Bezier curve
    for t in [i / 100.0 for i in range(101)]:  # 0 to 1 in 100 steps
        x = int((1 - t) ** 3 * p0[0] +
                 3 * (1 - t) ** 2 * t * p1[0] +
                 3 * (1 - t) * t ** 2 * p2[0] +
                 t ** 3 * p3[0])
        y = int((1 - t) ** 3 * p0[1] +
                 3 * (1 - t) ** 2 * t * p1[1] +
                 3 * (1 - t) * t ** 2 * p2[1] +
                 t ** 3 * p3[1])
        if 0 <= x < len(image[0]) and 0 <= y < len(image):  # Ensure within bounds
            image[y][x] = color  # Set pixel


def draw_line_with_sampling(image, start, end, color):
    x0, y0 = start
    x1, y1 = end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        # Sample 4 points for each pixel
        for dx_offset in [0.25, 0.75]:
            for dy_offset in [0.25, 0.75]:
                x_sample = int(x0 + dx_offset)
                y_sample = int(y0 + dy_offset)
                if 0 <= x_sample < len(image[0]) and 0 <= y_sample < len(image):
                    image[y_sample][x_sample] = color  # Set pixel

        if (x0 == x1) and (y0 == y1):
            break
        err2 = err * 2
        if err2 > -dy:
            err -= dy
            x0 += sx
        if err2 < dx:
            err += dx
            y0 += sy


def blend_colors(color1, color2, alpha):
    return (
        int(color1[0] * (1 - alpha) + color2[0] * alpha),
        int(color1[1] * (1 - alpha) + color2[1] * alpha),
        int(color1[2] * (1 - alpha) + color2[2] * alpha),
    )

def draw_line_with_anti_aliasing(image, start, end, color):
    x0, y0 = start
    x1, y1 = end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    # Draw line with anti-aliasing
    while True:
        alpha = 1  # Default alpha for main pixels
        if err > 0:
            alpha = 0.5  # Blend when close to edge
        elif err < 0:
            alpha = 0.5  # Blend when close to edge

        background_color = image[y0][x0]
        image[y0][x0] = blend_colors(color, background_color, alpha)  # Blend pixel colors

        if (x0 == x1) and (y0 == y1):
            break
        err2 = err * 2
        if err2 > -dy:
            err -= dy
            x0 += sx
        if err2 < dx:
            err += dx
            y0 += sy
