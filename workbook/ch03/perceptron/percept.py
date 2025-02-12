import os
import random

def generate_circle_image(size=8, noise_level=0.1):
    image = [[0] * size for _ in range(size)]
    cx, cy = random.randint(size // 4, 3 * size // 4), random.randint(size // 4, 3 * size // 4)
    radius = random.randint(size // 4, size // 3)
    
    for x in range(size):
        for y in range(size):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                image[x][y] = 1
    
    add_noise(image, noise_level)
    return image

def generate_square_image(size=8, noise_level=0.1):
    image = [[0] * size for _ in range(size)]
    start_x, start_y = random.randint(1, size // 3), random.randint(1, size // 3)
    end_x, end_y = random.randint(2 * size // 3, size - 1), random.randint(2 * size // 3, size - 1)
    
    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            image[x][y] = 1
    
    add_noise(image, noise_level)
    return image

def generate_line_image(size=8, noise_level=0.1):
    image = [[0] * size for _ in range(size)]
    slope = random.uniform(-1, 1)
    intercept = random.randint(0, size - 1)
    
    for x in range(size):
        y = int(slope * x + intercept)
        if 0 <= y < size:
            image[x][y] = 1
    
    add_noise(image, noise_level)
    return image

def add_noise(image, noise_level=0.1):
    size = len(image)
    num_pixels = int(size * size * noise_level)
    
    for _ in range(num_pixels):
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        image[x][y] = 1 if image[x][y] == 0 else 0

def flatten_image(image):
    return [pixel for row in image for pixel in row]

def save_image_ppm(image, filename):
    with open(filename, 'w') as f:
        f.write(f'P3\n{len(image[0])} {len(image)}\n255\n')
        for row in image:
            for pixel in row:
                f.write('255 255 255 ' if pixel == 1 else '0 0 0 ')
            f.write('\n')

def generate_and_save_data(num_samples=100, size=8):
    for folder in ["train/circle", "train/square", "train/line", "test/circle", "test/square", "test/line"]:
        os.makedirs(folder, exist_ok=True)

    for i in range(num_samples):
        for shape, folder in zip(["circle", "square", "line"], ["train/circle", "train/square", "train/line"]):
            image = globals()[f'generate_{shape}_image'](size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")
        
        for shape, folder in zip(["circle", "square", "line"], ["test/circle", "test/square", "test/line"]):
            image = globals()[f'generate_{shape}_image'](size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")


class Perceptron:
    def __init__(self, input_size, num_classes, l2_lambda=0.01):
        self.num_classes = num_classes
        self.input_size = input_size
        self.weights = [[random.uniform(-1, 1) for _ in range(input_size)] for _ in range(num_classes)]
        self.bias = [random.uniform(-1, 1) for _ in range(num_classes)]
        self.learning_rate = 0.1
        self.l2_lambda = l2_lambda  #regularization strength

    def activation(self, x):
        return 1 if x >= 0 else 0

    def predict(self, inputs):
        scores = [sum(w * i for w, i in zip(self.weights[c], inputs)) + self.bias[c] for c in range(self.num_classes)]
        return scores.index(max(scores))

    def train(self, training_data, labels, epochs):
        for _ in range(epochs):
            for inputs, label in zip(training_data, labels):
                prediction = self.predict(inputs)
                if prediction != label:
                    # update weights with L2 regularization
                    for i in range(len(self.weights[label])):
                        self.weights[label][i] += self.learning_rate * (inputs[i] - self.l2_lambda * self.weights[label][i])
                        self.weights[prediction][i] -= self.learning_rate * (inputs[i] + self.l2_lambda * self.weights[prediction][i])
                    # update biases
                    self.bias[label] += self.learning_rate
                    self.bias[prediction] -= self.learning_rate

def load_images_from_directory(directory, label):
    images, labels = [], []
    for filename in os.listdir(directory):
        if filename.endswith(".ppm"):
            with open(os.path.join(directory, filename), 'r') as f:
                lines = f.readlines()[3:]  # skip header
                pixels = [1 if int(val) > 127 else 0 for val in ' '.join(lines).split()]
                images.append(pixels)
                labels.append(label)
    return images, labels

def load_all_data():
    train_images, train_labels, test_images, test_labels = [], [], [], []
    
    for shape, label in zip(["circle", "square", "line"], [0, 1, 2]):
        img, lbl = load_images_from_directory(f"train/{shape}", label)
        train_images.extend(img)
        train_labels.extend(lbl)
        img, lbl = load_images_from_directory(f"test/{shape}", label)
        test_images.extend(img)
        test_labels.extend(lbl)
    
    return train_images, train_labels, test_images, test_labels


generate_and_save_data()

input_size = 64  # 8x8 image
perceptron = Perceptron(input_size, num_classes=3)
train_data, train_labels, test_data, test_labels = load_all_data()
perceptron.train(train_data, train_labels, epochs=10)

correct_predictions = sum(1 for inputs, label in zip(test_data, test_labels) if perceptron.predict(inputs) == label)
accuracy = correct_predictions / len(test_labels) * 100
print(f"Accuracy: {accuracy:.2f}%")

