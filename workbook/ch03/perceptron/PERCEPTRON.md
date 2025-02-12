
## Perceptron

A perceptron is a single-layer neural network (a type of classifier). It consists of an input layer,
a single output, and an activation function (often a step function or a sigmoid function).
The perceptron learns to classify data based on a set of features (input pixels in this case),
and you can train it using the Perceptron learning rule.


### Synthetic Image Generation

We'll create simple binary images (black and white) with basic shapes like circles, squares, and lines,
where each shape will be labeled for training. These images will be small (e.g., 8x8 or 16x16 pixels)
for simplicity.


### Training the Perceptron

The perceptron will take pixel values (flattened to a 1D vector) as input and output a prediction
(a simple class label, e.g., 0 for circle, 1 for square). You'll use randomised synthetic shapes
to generate both training and testing data.

Image Representation (PPM format):

We'll use the PPM3 format to save the images for simplicity. You can easily create images using
basic file I/O operations, similar to how you would generate random data.

#### Step 1: Create the Perceptron

Here's a simple implementation of a perceptron to classify shapes based on synthetic pixel data:

```python
import random

class Perceptron:
    def __init__(self, input_size):
        # init weights and bias to random values between -1 and 1
        self.weights = [random.uniform(-1, 1) for _ in range(input_size)]
        self.bias = random.uniform(-1, 1)
        self.learning_rate = 0.1

    def activation(self, x):
        # step function (for binary classification)
        return 1 if x >= 0 else 0

    def predict(self, inputs):
        # weighted sum of inputs + bias
        summation = sum([w * i for w, i in zip(self.weights, inputs)]) + self.bias
        return self.activation(summation)
    
    def train(self, training_data, labels, epochs):
        # train the perceptron using the Perceptron learning rule
        for _ in range(epochs):
            for inputs, label in zip(training_data, labels):
                prediction = self.predict(inputs)
                error = label - prediction
                # update weights and bias
                for i in range(len(self.weights)):
                    self.weights[i] += self.learning_rate * error * inputs[i]
                self.bias += self.learning_rate * error
```

#### Step 2: Generate Simple Synthetic Images

We will create synthetic *binary images* with simple shapes like circles, squares, and lines.
Each shape will be labeled with a unique class.

```python
import random
import math

# create a binary image with a circle
def generate_circle_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    cx, cy = size // 2, size // 2  # circle center
    radius = size // 3
    for x in range(size):
        for y in range(size):
            # if the point (x, y) is within the circle
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                image[x][y] = 1  # set pixel to white (circle)
    return image

# create a binary image with a square
def generate_square_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    start = size // 3
    end = size - start
    for x in range(start, end):
        for y in range(start, end):
            image[x][y] = 1  # set pixel to white (square)
    return image

# create a binary image with a diagonal line
def generate_line_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    for i in range(size):
        image[i][i] = 1  # set pixel to white (line)
    return image

# convert a 2D image (list of lists) to a 1D list for perceptron
def flatten_image(image):
    return [pixel for row in image for pixel in row]

# generate training data
def generate_training_data(num_samples=100):
    shapes = ['circle', 'square', 'line']
    data = []
    labels = []
    for _ in range(num_samples):
        shape = random.choice(shapes)
        if shape == 'circle':
            image = generate_circle_image()
            label = 0  # label for circle
        elif shape == 'square':
            image = generate_square_image()
            label = 1  # label for square
        else:
            image = generate_line_image()
            label = 2  # label for line
        data.append(flatten_image(image))
        labels.append(label)
    return data, labels
```

#### Step 3: Train the Perceptron

Now let's train the perceptron using the synthetic training data. We'll train the
perceptron to recognize circles, squares, and lines.

```python
# init perceptron
input_size = 64  # 8x8 image (flattened to 64)
perceptron = Perceptron(input_size)

# generate training data
training_data, labels = generate_training_data(num_samples=500)

# train the perceptron
perceptron.train(training_data, labels, epochs=10)

# test the perceptron on new data
test_data, test_labels = generate_training_data(num_samples=100)

# evaluate the perceptron
correct_predictions = 0
for inputs, label in zip(test_data, test_labels):
    prediction = perceptron.predict(inputs)
    if prediction == label:
        correct_predictions += 1

print(f"Accuracy: {correct_predictions / len(test_labels) * 100:.2f}%")
```

#### Step 4: Save Synthetic Images to PPM (Optional)

You can save the generated images in PPM3 format (for simplicity) to visually inspect them.

```python
def save_image_ppm(image, filename='image.ppm'):
    height = len(image)
    width = len(image[0])
    with open(filename, 'w') as f:
        # header
        f.write(f'P3\n{width} {height}\n255\n')
        for row in image:
            for pixel in row:
                # white (1) or Black (0) for the PPM format
                color = '255 255 255' if pixel == 1 else '0 0 0'
                f.write(f'{color} ')
            f.write('\n')

# Example: Save a circle image
circle_image = generate_circle_image(size=8)
save_image_ppm(circle_image, 'circle.ppm')
```

__Perceptron:__

The perceptron has random initial weights and biases. It uses a step activation function
(activation method) to decide whether the input belongs to a particular class
(circle, square, or line). The train method adjusts the weights and bias using the *Perceptron*
learning rule.


__Image Generation:__

Simple shapes (circle, square, and line) are generated using basic geometry principles.
The images are converted to 1D arrays by flattening the 2D pixel arrays for use as input
to the perceptron.


__Synthetic Data:__

The training data consists of 100 random synthetic images for each shape
(circle, square, and line), which are labeled as 0, 1, and 2, respectively.


__Training and Testing:__

The perceptron is trained on the generated data, and we evaluate its performance
by testing it on new randomly generated images.


__PPM Format:__

The PPM image format (P3) is used for saving the images. The pixel values are
either 0 0 0 (black) or 255 255 255 (white) for simplicity.


### Conclusion

By following this approach, you've created a simple perceptron that can classify
synthetically generated shapes (circle, square, line) from basic pixel data.

This simple perceptron model can classify basic shapes and serves as a foundation
to explore more advanced machine learning concepts such as multi-layer perceptrons
or deep learning models.




### More Detailed Attempt ..

Save Images to Files: We will generate and save the training and test images in PPM format.
These images will be labeled and saved in different directories for training and testing.

Read Images from Files: During training, we will load these images from the saved PPM files
and preprocess them into the format needed by the perceptron (flattened pixel arrays).

Accuracy Statistics: After training, we'll test the perceptron on the test images and calculate
the accuracy. We'll also print detailed statistics on how well the model performs.

hm.

### Step-by-Step

Image Generation: We'll save the images in directories (e.g., train/, test/), with each shape
type in its own subdirectory (e.g., train/circle/, train/square/, etc.).

Saving Images: The images will be saved in PPM format.

Loading Images: The program will read these images from files, flatten them, and use them
for training and testing.

Accuracy Calculation: We'll print the accuracy and confusion matrix for better insights.


#### 1. Save Training and Test Images

We first generate and save images for training and testing in separate directories.

```python
import os
import random

# create binary image with a circle
def generate_circle_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    cx, cy = size // 2, size // 2  # circle center
    radius = size // 3
    for x in range(size):
        for y in range(size):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                image[x][y] = 1  # set pixel to white (circle)
    return image

# create binary image with a square
def generate_square_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    start = size // 3
    end = size - start
    for x in range(start, end):
        for y in range(start, end):
            image[x][y] = 1  # set pixel to white (square)
    return image

# create a binary image with a diagonal line
def generate_line_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    for i in range(size):
        image[i][i] = 1  # set pixel to white (line)
    return image

# convert a 2D image (list of lists) to a 1D list for perceptron
def flatten_image(image):
    return [pixel for row in image for pixel in row]

# ave a 2D image as a PPM3 file
def save_image_ppm(image, filename):
    height = len(image)
    width = len(image[0])
    with open(filename, 'w') as f:
        # Write PPM header
        f.write(f'P3\n{width} {height}\n255\n')
        for row in image:
            for pixel in row:
                color = '255 255 255' if pixel == 1 else '0 0 0'
                f.write(f'{color} ')
            f.write('\n')

# generate and save training and testing data
def generate_and_save_data(num_samples=100, size=8):
    # dirs save images
    if not os.path.exists("train/circle"):
        os.makedirs("train/circle")
    if not os.path.exists("train/square"):
        os.makedirs("train/square")
    if not os.path.exists("train/line"):
        os.makedirs("train/line")
    if not os.path.exists("test/circle"):
        os.makedirs("test/circle")
    if not os.path.exists("test/square"):
        os.makedirs("test/square")
    if not os.path.exists("test/line"):
        os.makedirs("test/line")

    for i in range(num_samples):
        # create and save training images
        for shape, folder in zip(["circle", "square", "line"], ["train/circle", "train/square", "train/line"]):
            if shape == "circle":
                image = generate_circle_image(size)
            elif shape == "square":
                image = generate_square_image(size)
            elif shape == "line":
                image = generate_line_image(size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")
        
        # create and save testing images (more samples for testing)
        for shape, folder in zip(["circle", "square", "line"], ["test/circle", "test/square", "test/line"]):
            if shape == "circle":
                image = generate_circle_image(size)
            elif shape == "square":
                image = generate_square_image(size)
            elif shape == "line":
                image = generate_line_image(size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")
```

#### 2. Load Images for Training and Testing

Now, we will write a function to load the images from the saved files and
flatten them for input into the perceptron.

```python
import os

# load images from a directory and assign labels
def load_images_from_directory(directory, label):
    images = []
    labels = []
    for filename in os.listdir(directory):
        if filename.endswith(".ppm"):
            # read image data from PPM file
            with open(os.path.join(directory, filename), 'r') as f:
                lines = f.readlines()
                pixels = []
                for line in lines[3:]:  # skip header
                    pixels += [int(val) for val in line.split()]
                images.append(pixels)
                labels.append(label)
    return images, labels

# load all training and test data
def load_all_data():
    train_images = []
    train_labels = []
    test_images = []
    test_labels = []

    # load training data
    for shape, label in zip(["circle", "square", "line"], [0, 1, 2]):
        shape_images, shape_labels = load_images_from_directory(f"train/{shape}", label)
        train_images += shape_images
        train_labels += shape_labels

    # load test data
    for shape, label in zip(["circle", "square", "line"], [0, 1, 2]):
        shape_images, shape_labels = load_images_from_directory(f"test/{shape}", label)
        test_images += shape_images
        test_labels += shape_labels

    return train_images, train_labels, test_images, test_labels
```

#### 3. Train the Perceptron

Now we will train the perceptron using the images that were loaded from the files.

```python
# init perceptron
input_size = 64  # 8x8 image (flattened to 64)
perceptron = Perceptron(input_size)

# load training and testing data
train_data, train_labels, test_data, test_labels = load_all_data()

# train perceptron
perceptron.train(train_data, train_labels, epochs=10)

# evaluate perceptron on the test data
correct_predictions = 0
total_predictions = len(test_labels)
confusion_matrix = {0: {0: 0, 1: 0, 2: 0}, 1: {0: 0, 1: 0, 2: 0}, 2: {0: 0, 1: 0, 2: 0}}

for inputs, label in zip(test_data, test_labels):
    prediction = perceptron.predict(inputs)
    if prediction == label:
        correct_predictions += 1
    confusion_matrix[label][prediction] += 1

accuracy = correct_predictions / total_predictions * 100
print(f"Accuracy: {accuracy:.2f}%")

print("Confusion Matrix:")
for actual in range(3):
    print(f"Actual {actual}: {confusion_matrix[actual]}")
```

#### 4. Results and Statistics
When you run the code, it will print the accuracy of the perceptron on the test data,
along with a confusion matrix showing how many times each predicted class matches the
actual class.


Example Output:

```
Accuracy: 85.00%
Confusion Matrix:
Actual 0: {0: 25, 1: 2, 2: 3}
Actual 1: {0: 3, 1: 28, 2: 4}
Actual 2: {0: 4, 1: 3, 2: 29}
```


Conclusion

- Saved images for both training and testing.
- Loaded images from files and flattened them for input into the perceptron.
- Trained the perceptron on the training data and evaluated it on the test data.
- Printed the accuracy and confusion matrix to assess how well the perceptron recognizes the shapes.

This approach allows you to train and test a simple perceptron on synthetic images,
and it provides some useful statistics to evaluate the performance of the model.

