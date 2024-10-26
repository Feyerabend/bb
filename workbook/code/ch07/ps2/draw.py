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
