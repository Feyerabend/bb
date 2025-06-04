# GAN for CIFAR-10 Image Generation
import tensorflow as tf
import numpy as np
from PIL import Image  # For saving images

# Set random seed for reproducibility
tf.random.set_seed(42)
np.random.seed(42)

# Load and preprocess CIFAR-10 dataset
(x_train, _), (_, _) = tf.keras.datasets.cifar10.load_data()
x_train = x_train.astype('float32') / 255.0  # Normalize to [0, 1]
x_train = (x_train - 0.5) / 0.5  # Scale to [-1, 1] for better GAN training

# Define the Generator
def build_generator():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(4 * 4 * 256, input_dim=100, activation='relu'),
        tf.keras.layers.Reshape((4, 4, 256)),
        tf.keras.layers.Conv2DTranspose(128, (4, 4), strides=(2, 2), padding='same', activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same', activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Conv2DTranspose(32, (4, 4), strides=(2, 2), padding='same', activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Conv2D(3, (3, 3), padding='same', activation='tanh')  # Output: 32x32x3
    ])
    return model

# Define the Discriminator
def build_discriminator():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(64, (3, 3), strides=(2, 2), padding='same', input_shape=(32, 32, 3), activation='relu'),
        tf.keras.layers.LeakyReLU(alpha=0.2),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Conv2D(128, (3, 3), strides=(2, 2), padding='same', activation='relu'),
        tf.keras.layers.LeakyReLU(alpha=0.2),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Conv2D(256, (3, 3), strides=(2, 2), padding='same', activation='relu'),
        tf.keras.layers.LeakyReLU(alpha=0.2),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

# Loss function
cross_entropy = tf.keras.losses.BinaryCrossentropy()

# Discriminator loss
def discriminator_loss(real_output, fake_output):
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    return real_loss + fake_loss

# Generator loss
def generator_loss(fake_output):
    return cross_entropy(tf.ones_like(fake_output), fake_output)

# Optimizers
generator_optimizer = tf.keras.optimizers.Adam(1e-4, beta_1=0.5)
discriminator_optimizer = tf.keras.optimizers.Adam(1e-4, beta_1=0.5)

# Build models
generator = build_generator()
discriminator = build_discriminator()

# Function to save generated images as a grid using Pillow
def save_generated_images(images, epoch, grid_size=(4, 4)):
    images = (images * 0.5) + 0.5  # Rescale from [-1, 1] to [0, 1]
    images = np.clip(images, 0, 1)  # Ensure pixel values are valid
    images = (images * 255).astype(np.uint8)  # Convert to uint8 for Pillow
    
    grid_rows, grid_cols = grid_size
    img_size = 32  # CIFAR-10 image size
    grid_img = Image.new('RGB', (grid_cols * img_size, grid_rows * img_size))
    
    for i in range(min(grid_rows * grid_cols, len(images))):
        row = i // grid_cols
        col = i % grid_cols
        img = Image.fromarray(images[i])
        grid_img.paste(img, (col * img_size, row * img_size))
    
    grid_img.save(f'generated_epoch_{epoch}.png')
    print(f'Saved generated images for epoch {epoch} as generated_epoch_{epoch}.png')

# Training step
@tf.function
def train_step(images, batch_size, noise_dim):
    noise = tf.random.normal([batch_size, noise_dim])

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
        generated_images = generator(noise, training=True)
        
        real_output = discriminator(images, training=True)
        fake_output = discriminator(generated_images, training=True)
        
        gen_loss = generator_loss(fake_output)
        disc_loss = discriminator_loss(real_output, fake_output)
    
    gen_gradients = gen_tape.gradient(gen_loss, generator.trainable_variables)
    disc_gradients = disc_tape.gradient(disc_loss, discriminator.trainable_variables)
    
    generator_optimizer.apply_gradients(zip(gen_gradients, generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(disc_gradients, discriminator.trainable_variables))
    
    return gen_loss, disc_loss

# Training loop
def train(dataset, epochs, batch_size=128, noise_dim=100):
    for epoch in range(epochs):
        for image_batch in dataset:
            gen_loss, disc_loss = train_step(image_batch, batch_size, noise_dim)
        
        # Print progress
        print(f'Epoch {epoch + 1}, Gen Loss: {gen_loss:.4f}, Disc Loss: {disc_loss:.4f}')
        
        # Generate and save sample images every 10 epochs
        if (epoch + 1) % 10 == 0:
            noise = tf.random.normal([16, noise_dim])
            generated_images = generator(noise, training=False)
            save_generated_images(generated_images.numpy(), epoch + 1)

# Prepare dataset
batch_size = 128
dataset = tf.data.Dataset.from_tensor_slices(x_train).shuffle(50000).batch(batch_size)

# Train the GAN
train(dataset, epochs=50, batch_size=batch_size, noise_dim=100)
