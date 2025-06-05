import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# CIFAR-10 class names
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 
               'dog', 'frog', 'horse', 'ship', 'truck']

def create_model():
    """Create and compile the CNN model"""
    model = keras.Sequential([
        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Third convolutional block
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.25),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(10, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_or_load_model():
    """Train a new model or load existing one"""
    model_path = 'cifar10_model.h5'
    
    if os.path.exists(model_path):
        print("Loading existing model...")
        model = keras.models.load_model(model_path)
    else:
        print("Training new model...")
        # Load and preprocess CIFAR-10 data
        (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
        
        x_train = x_train.astype('float32') / 255.0
        x_test = x_test.astype('float32') / 255.0
        
        y_train = keras.utils.to_categorical(y_train, 10)
        y_test = keras.utils.to_categorical(y_test, 10)
        
        # Create and train model
        model = create_model()
        
        # Data augmentation
        datagen = keras.preprocessing.image.ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True,
            zoom_range=0.1
        )
        datagen.fit(x_train)
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.2, patience=5, min_lr=0.0001)
        ]
        
        # Train
        history = model.fit(
            datagen.flow(x_train, y_train, batch_size=32),
            steps_per_epoch=len(x_train) // 32,
            epochs=50,
            validation_data=(x_test, y_test),
            callbacks=callbacks,
            verbose=1
        )
        
        # Save model
        model.save(model_path)
        print(f"Model saved to {model_path}")
        
        # Evaluate
        test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
        print(f"Test accuracy: {test_accuracy:.4f}")
    
    return model

def preprocess_image(image_path):
    """Load and preprocess a custom image for prediction"""
    try:
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to 32x32 (CIFAR-10 size)
        img = img.resize((32, 32), Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize
        img_array = np.array(img).astype('float32') / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array, img
    
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

def predict_image(model, image_path, show_image=True):
    """Predict the class of a custom image"""
    # Preprocess image
    processed_img, original_img = preprocess_image(image_path)
    
    if processed_img is None:
        return None
    
    # Make prediction
    predictions = model.predict(processed_img, verbose=0)
    predicted_probs = predictions[0]
    
    # Get top 3 predictions
    top_indices = np.argsort(predicted_probs)[::-1][:3]
    
    # Display results
    print(f"\nPredictions for {os.path.basename(image_path)}:")
    print("-" * 40)
    
    for i, idx in enumerate(top_indices):
        confidence = predicted_probs[idx] * 100
        print(f"{i+1}. {class_names[idx]}: {confidence:.2f}%")
    
    if show_image:
        # Display original and resized image
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 3, 1)
        plt.imshow(original_img)
        plt.title('Original Image')
        plt.axis('off')
        
        plt.subplot(1, 3, 2)
        plt.imshow(processed_img[0])
        plt.title('Resized to 32x32')
        plt.axis('off')
        
        plt.subplot(1, 3, 3)
        # Bar chart of predictions
        plt.bar(range(len(class_names)), predicted_probs)
        plt.xticks(range(len(class_names)), class_names, rotation=45)
        plt.ylabel('Probability')
        plt.title('Prediction Probabilities')
        plt.tight_layout()
        
        plt.show()
    
    return {
        'predictions': [(class_names[idx], predicted_probs[idx]) for idx in top_indices],
        'all_probabilities': dict(zip(class_names, predicted_probs))
    }

def predict_multiple_images(model, image_paths):
    """Predict multiple images at once"""
    results = []
    
    for image_path in image_paths:
        if os.path.exists(image_path):
            result = predict_image(model, image_path, show_image=False)
            if result:
                results.append({
                    'image_path': image_path,
                    'top_prediction': result['predictions'][0],
                    'all_predictions': result['predictions']
                })
        else:
            print(f"Image not found: {image_path}")
    
    return results

# Main execution
if __name__ == "__main__":
    print("CIFAR-10 Image Classifier")
    print("=" * 50)
    
    # Load or train model
    model = train_or_load_model()
    
    # Example usage - replace with your image paths
    print("\nExample usage:")
    print("1. Single image prediction:")
    
    # Example image paths (replace with your actual image paths)
    example_images = [
        "images/cat.png",
#        "images/airplane.jpg", 
#        "images/car.jpg"
    ]
    
    print("# To predict a single image:")
    print("result = predict_image(model, 'path/to/your/image.jpg')")
    print()
    print("# To predict multiple images:")
    print("results = predict_multiple_images(model, ['image1.jpg', 'image2.jpg'])")
    print()
    
    # If you have actual images, uncomment and modify these lines:
    # result = predict_image(model, "your_image.jpg")
    # results = predict_multiple_images(model, ["image1.jpg", "image2.jpg"])
    
    print("Instructions:")
    print("1. Save this script as 'cifar10_predictor.py'")
    print("2. Place your images in the same directory or provide full paths")
    print("3. Call predict_image(model, 'your_image.jpg') to get predictions")
    print("4. The script will show the original image, resized version, and probability bars")
    print("5. It will print the top 3 most likely classes with confidence percentages")

# Additional utility function for batch processing
def batch_predict_from_folder(model, folder_path, image_extensions=('.jpg', '.jpeg', '.png', '.bmp')):
    """Predict all images in a folder"""
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return []
    
    image_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(image_extensions):
            image_files.append(os.path.join(folder_path, file))
    
    if not image_files:
        print("No image files found in the folder")
        return []
    
    print(f"Found {len(image_files)} images to process...")
    results = predict_multiple_images(model, image_files)
    
    # Summary
    print(f"\nSummary of {len(results)} predictions:")
    print("-" * 50)
    for result in results:
        filename = os.path.basename(result['image_path'])
        top_class, confidence = result['top_prediction']
        print(f"{filename}: {top_class} ({confidence*100:.1f}%)")
    
    return results