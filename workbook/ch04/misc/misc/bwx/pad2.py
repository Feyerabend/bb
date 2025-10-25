from PIL import Image
import os

def convert_bmp(input_path, output_path):
    # Open the input image
    img = Image.open(input_path)
    
    # Verify input image is 240x240
    if img.size != (240, 240):
        raise ValueError(f"Input image must be 240x240, got {img.size}")
    
    # Determine the mode for the new image
    output_mode = img.mode if img.mode in ('1', 'L') else 'RGB'
    
    # Define white color based on mode
    white_color = 255 if output_mode in ('1', 'L') else (255, 255, 255)
    
    # Create a new 320x240 image with white background
    new_img = Image.new(output_mode, (320, 240), white_color)
    
    # If input is 1-bit, ensure it remains 1-bit during paste
    if img.mode == '1':
        # Convert input image to 1-bit explicitly if needed
        img = img.convert('1')
    
    # Calculate paste position to center the original image
    paste_x = (320 - 240) // 2  # 40 pixels padding on each side
    paste_y = 0
    
    # Paste the original image in the center
    new_img.paste(img, (paste_x, paste_y))
    
    # Save the new image as BMP with appropriate format
    if output_mode == '1':
        # Save as 1-bit BMP explicitly
        new_img.save(output_path, 'BMP', bits=1)
    else:
        new_img.save(output_path, 'BMP')

def process_directory(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all BMP files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.bmp'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            try:
                convert_bmp(input_path, output_path)
                print(f"Converted {filename} (Mode: {Image.open(input_path).mode} -> {Image.open(output_path).mode})")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

# Example usage
if __name__ == "__main__":
    input_directory = "input_images"
    output_directory = "output_images"
    process_directory(input_directory, output_directory)