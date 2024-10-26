def draw_line(image, start, end, color, sample_rate=4):
    x0, y0 = start
    x1, y1 = end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        # Draw with anti-aliasing by sampling around the pixel center
        for dx in range(sample_rate):
            for dy in range(sample_rate):
                # Calculate the offset for supersampling
                offset_x = (dx + 0.5) / sample_rate
                offset_y = (dy + 0.5) / sample_rate

                # Get the final coordinates for the subpixel
                final_x = x0 + offset_x
                final_y = y0 + offset_y

                if 0 <= int(final_x) < len(image[0]) and 0 <= int(final_y) < len(image):  # ensure within bounds
                    # Calculate the distance from the center of the pixel
                    distance = ((offset_x - 0.5) ** 2 + (offset_y - 0.5) ** 2) ** 0.5
                    alpha = max(0, 1 - distance * 2)  # Blend factor

                    current_color = image[int(final_y)][int(final_x)]

                    # Simple linear interpolation for color blending
                    blended_color = tuple(
                        int((1 - alpha) * current_color[i] + alpha * color[i]) for i in range(3)
                    )

                    image[int(final_y)][int(final_x)] = blended_color  # set pixel with blended color

        if (x0 == x1) and (y0 == y1):
            break

        err2 = err * 2
        if err2 > -dy:
            err -= dy
            x0 += sx
        if err2 < dx:
            err += dx
            y0 += sy

def draw_bezier_curve(image, p0, p1, p2, color, sample_rate=4):
    # calculate points on a quadratic Bezier curve with anti-aliasing
    for t in [i / (sample_rate * 100.0) for i in range(sample_rate * 101)]:  # 0 to 1 in higher steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]

        # Calculate the integer pixel coordinates
        x0, y0 = int(x), int(y)

        # Set color with blending based on distance
        for dx in range(sample_rate):
            for dy in range(sample_rate):
                # Calculate the offset for supersampling
                offset_x = (dx + 0.5) / sample_rate
                offset_y = (dy + 0.5) / sample_rate

                # Get the final coordinates for the subpixel
                final_x = int(x0 + offset_x)
                final_y = int(y0 + offset_y)

                if 0 <= final_x < len(image[0]) and 0 <= final_y < len(image):  # ensure within bounds
                    # Calculate the contribution based on how close the sample point is to the pixel center
                    distance = ((offset_x - 0.5) ** 2 + (offset_y - 0.5) ** 2) ** 0.5
                    alpha = max(0, 1 - distance * 2)  # Blend factor
                    current_color = image[final_y][final_x]

                    # Simple linear interpolation for color blending
                    blended_color = tuple(
                        int((1 - alpha) * current_color[i] + alpha * color[i]) for i in range(3)
                    )

                    image[final_y][final_x] = blended_color  # set pixel with blended color
