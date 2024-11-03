from PIL import Image, ImageDraw, ImageFont

# Example dataset with (x, y) points and labels
dataset = [
    (1.0, 1.0, 0),
    (2.0, 2.0, 0),
    (3.0, 3.0, 0),
    (6.0, 6.0, 1),
    (7.0, 7.0, 1),
    (8.0, 8.0, 1),
    (9.0, 9.0, 1),
    (5.0, 5.0, 0)
]

# New point to classify
new_point = (4.0, 4.5)
#new_point = (4.0, 6.5)

# Create a blank image
img_size = (400, 400)
background_color = (255, 255, 255)
image = Image.new("RGB", img_size, background_color)
draw = ImageDraw.Draw(image)

# Scale factors for plotting
x_scale = img_size[0] / 10  # Scale x-axis to fit the image width
y_scale = img_size[1] / 10  # Scale y-axis to fit the image height

# Define colors for labels and background shading
colors = {
    0: (200, 200, 255, 100),  # Blue for label 0
    1: (255, 200, 200, 100)   # Red for label 1
}

# Fill areas for each class
for i in range(img_size[0]):
    for j in range(img_size[1]):
        # Map pixel coordinates to (x, y) space
        x = i * 10 / img_size[0]
        y = j * 10 / img_size[1]
        
        # Count the number of neighbors in each class for this point
        distances = []
        for point in dataset:
            distance = ((x - point[0]) ** 2 + (y - point[1]) ** 2) ** 0.5
            distances.append((distance, point[2]))  # (distance, label)
        
        # Sort by distance and take the first k neighbors
        k = 3
        distances.sort(key=lambda x: x[0])
        nearest_labels = [label for _, label in distances[:k]]
        
        # Determine the majority class
        majority_label = max(set(nearest_labels), key=nearest_labels.count)
        fill_color = colors[majority_label]
        
        # Draw the pixel
        draw.point((i, j), fill=(fill_color[0], fill_color[1], fill_color[2]))

# Draw the training points
for x, y, label in dataset:
    draw.ellipse([(x * x_scale - 5, y * y_scale - 5), (x * x_scale + 5, y * y_scale + 5)],
                 fill=(colors[label][0], colors[label][1], colors[label][2]), outline=(0, 0, 0))
    draw.text((x * x_scale + 7, y * y_scale - 5), f'({x}, {y})', fill=(0, 0, 0))

# Draw the new point
new_x, new_y = new_point
draw.ellipse([(new_x * x_scale - 10, new_y * y_scale - 10), 
               (new_x * x_scale + 10, new_y * y_scale + 10)],
             fill=(0, 255, 0), outline=(0, 0, 0))  # Green for new point
draw.text((new_x * x_scale + 7, new_y * y_scale - 15), f'New Point\n({new_x}, {new_y})', fill=(0, 0, 0))

# Draw axes
# X-axis: from (0, height/10) to (width, height/10)
draw.line([(0, img_size[1] - (img_size[1] / 10)), (img_size[0], img_size[1] - (img_size[1] / 10))], fill=(0, 0, 0), width=1)
# Y-axis: from (width/10, 0) to (width/10, height)
draw.line([(img_size[0] / 10, 0), (img_size[0] / 10, img_size[1])], fill=(0, 0, 0), width=1)

# Save the image as PNG
image.save('knn_classification_with_boundary.png')
image.show()  # Display the image