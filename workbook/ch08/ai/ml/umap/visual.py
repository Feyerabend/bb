from PIL import Image, ImageDraw
import csv

# Read data
X, Y, labels = [], [], []
with open("umap_data.txt", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        X.append([float(row["X1"]), float(row["X2"]), float(row["X3"])])
        Y.append([float(row["Y1"]), float(row["Y2"])])
        labels.append(int(row["Label"]))

# Normalize Y to [0, 400]
Y = [[y[0] for y in Y], [y[1] for y in Y]]
Y[0] = [(y - min(Y[0])) / (max(Y[0]) - min(Y[0]) + 1e-8) * 400 for y in Y[0]]
Y[1] = [(y - min(Y[1])) / (max(Y[1]) - min(Y[1]) + 1e-8) * 400 for y in Y[1]]

# Create image
img = Image.new("RGB", (500, 500), "white")
draw = ImageDraw.Draw(img)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

# Draw points
for i in range(len(Y[0])):
    x, y = Y[0][i], Y[1][i]
    draw.ellipse([(x - 3, y - 3), (x + 3, y + 3)], fill=colors[labels[i]])

img.save("umap_output.png")
print("Visualization saved as umap_output.png")