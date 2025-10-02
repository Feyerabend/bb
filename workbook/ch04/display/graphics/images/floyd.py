def read_ppm(filename):
    with open(filename, 'r') as f:
        header = f.readline().strip()
        if header != 'P3':
            raise ValueError("Not a valid PPM file.")
        dimensions = f.readline().strip()
        width, height = map(int, dimensions.split())
        max_color_value = int(f.readline().strip())
        
        pixels = []
        for line in f:
            pixels.extend(map(int, line.split()))
        
        # Convert flat list to a list of lists (height x width x RGB)
        image = []
        for i in range(height):
            row = []
            for j in range(width):
                pixel = (pixels[(i * width + j) * 3], 
                          pixels[(i * width + j) * 3 + 1], 
                          pixels[(i * width + j) * 3 + 2])
                row.append(pixel)
            image.append(row)

        return image, width, height, max_color_value

def write_ppm(filename, pixels, max_color_value):
    height = len(pixels)
    width = len(pixels[0])
    with open(filename, 'w') as f:
        f.write("P3\n")
        f.write(f"{width} {height}\n")
        f.write(f"{max_color_value}\n")
        for row in pixels:
            for pixel in row:
                f.write(f"{pixel[0]} {pixel[1]} {pixel[2]} ")
            f.write("\n")

def floyd_steinberg_dithering(image):
    height = len(image)
    width = len(image[0])
    dithered_image = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            old_pixel = image[y][x]
            new_pixel = [round(color / 255) * 255 for color in old_pixel]
            dithered_image[y][x] = new_pixel
            
            error = [old_pixel[i] - new_pixel[i] for i in range(3)]

            if x + 1 < width:
                image[y][x + 1] = [min(max(0, image[y][x + 1][i] + error[i] * 7 / 16), 255) for i in range(3)]
            if x - 1 >= 0 and y + 1 < height:
                image[y + 1][x - 1] = [min(max(0, image[y + 1][x - 1][i] + error[i] * 3 / 16), 255) for i in range(3)]
            if y + 1 < height:
                image[y + 1][x] = [min(max(0, image[y + 1][x][i] + error[i] * 5 / 16), 255) for i in range(3)]
            if x + 1 < width and y + 1 < height:
                image[y + 1][x + 1] = [min(max(0, image[y + 1][x + 1][i] + error[i] * 1 / 16), 255) for i in range(3)]

    return dithered_image

def main(input_file, output_file):
    image, width, height, max_color_value = read_ppm(input_file)
    dithered_image = floyd_steinberg_dithering(image)
    write_ppm(output_file, dithered_image, max_color_value)

if __name__ == "__main__":
    input_filename = 'input.ppm'  # Change to your input file name
    output_filename = 'output.ppm'  # Change to your desired output file name
    main(input_filename, output_filename)
