# ppm_reader.py
def read_ppm(filename):
    with open(filename, 'r') as f:
        # Read PPM header
        header = f.readline().strip()
        if header != 'P3':
            raise ValueError("File is not in PPM P3 format")
        
        # Read image dimensions
        dimensions = f.readline().strip()
        width, height = map(int, dimensions.split())
        
        # Read max color value
        max_color_value = int(f.readline().strip())
        
        # Read pixel data
        pixel_data = []
        for line in f:
            pixel_data.extend(map(int, line.strip().split()))
        
        # Convert pixel data into 2D array
        image = []
        for i in range(height):
            row = []
            for j in range(width):
                r = pixel_data[(i * width + j) * 3]
                g = pixel_data[(i * width + j) * 3 + 1]
                b = pixel_data[(i * width + j) * 3 + 2]
                row.append((r, g, b))
            image.append(row)
        
        return width, height, image