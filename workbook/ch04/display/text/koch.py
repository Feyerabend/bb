import math

# Function to generate the Koch curve for one side of the snowflake
def koch_curve(points, iterations):
    if iterations == 0:
        return points

    new_points = []
    for i in range(len(points) - 1):
        # Start and end points of the current segment
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        
        # Calculate new points that divide the line into four segments
        dx = (x2 - x1) / 3
        dy = (y2 - y1) / 3
        
        # Points at 1/3 and 2/3 along the line segment
        p1 = (x1 + dx, y1 + dy)
        p2 = (x1 + 2 * dx, y1 + 2 * dy)
        
        # Calculate the peak of the equilateral triangle
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        peak_x = mid_x - dy * math.sqrt(3) / 2
        peak_y = mid_y + dx * math.sqrt(3) / 2
        p3 = (peak_x, peak_y)
        
        # Append new points to form the Koch curve
        new_points.extend([points[i], p1, p3, p2])
    new_points.append(points[-1])

    # Recurse for the next iteration
    return koch_curve(new_points, iterations - 1)

# Function to create a PPM image from the Koch snowflake points
def generate_ppm_snowflake(filename, iterations, image_size):
    # Define the initial equilateral triangle
    size = image_size / 3  # Scale factor for the triangle
    angle = math.pi / 3    # 60 degrees in radians
    points = [
        (size, 0),
        (size * math.cos(angle), size * math.sin(angle)),
        (size * math.cos(2 * angle), size * math.sin(2 * angle)),
        (size, 0)
    ]

    # Generate Koch curves for each side of the triangle
    snowflake_points = []
    for i in range(3):
        rotated_points = rotate_points(points, i * 2 * math.pi / 3)
        snowflake_points += koch_curve(rotated_points, iterations)

    # Transform points to fit in the image space
    transformed_points = [(int(x + image_size / 2), int(y + image_size / 3)) for x, y in snowflake_points]

    # Create a blank white image
    pixels = [[(255, 255, 255) for _ in range(image_size)] for _ in range(image_size)]

    # Draw the snowflake points onto the image as black pixels
    for x, y in transformed_points:
        if 0 <= x < image_size and 0 <= y < image_size:
            pixels[y][x] = (0, 0, 0)

    # Save the pixels as a PPM file
    with open(filename, "w") as f:
        f.write(f"P3\n{image_size} {image_size}\n255\n")
        for row in pixels:
            for r, g, b in row:
                f.write(f"{r} {g} {b} ")
            f.write("\n")

# Helper function to rotate points around the origin
def rotate_points(points, angle):
    return [(x * math.cos(angle) - y * math.sin(angle),
             x * math.sin(angle) + y * math.cos(angle)) for x, y in points]

# Run the function to generate a PPM image of the Koch snowflake
generate_ppm_snowflake("koch_snowflake.ppm", iterations=4, image_size=600)
