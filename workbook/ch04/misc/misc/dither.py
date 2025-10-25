import os

class Dither:
    def __init__(self, input_file, output_file="output.ppm"):
        self.input_file = input_file
        self.output_file = output_file
        self.image, self.width, self.height = self.load_ppm(self.input_file)
        self.apply_dithering()
        self.save_ppm(self.output_file)

    def load_ppm(self, filename):
        with open(filename, 'r') as f:
            # Read header
            assert f.readline().strip() == 'P3'  # P3 means ASCII PPM
            width, height = map(int, f.readline().strip().split())
            max_val = int(f.readline().strip())  # Max color value, typically 255

            # Read pixel data
            pixels = []
            for line in f:
                pixels.extend(map(int, line.split()))

            # Convert flat list to list of tuples (R, G, B)
            image = [(pixels[i], pixels[i+1], pixels[i+2]) for i in range(0, len(pixels), 3)]
        
        return image, width, height

    def save_ppm(self, filename):
        with open(filename, 'w') as f:
            f.write("P3\n")
            f.write(f"{self.width} {self.height}\n255\n")
            for pixel in self.image:
                f.write(f"{pixel[0]} {pixel[1]} {pixel[2]}\n")

    def apply_threshold(self, value):
        return 255 if value > 128 else 0

    def apply_dithering(self):
        for y in range(self.height):
            for x in range(self.width):
                idx = y * self.width + x
                old_pixel = self.image[idx]
                new_pixel = (
                    self.apply_threshold(old_pixel[0]),
                    self.apply_threshold(old_pixel[1]),
                    self.apply_threshold(old_pixel[2])
                )
                self.image[idx] = new_pixel

                # Calculate the error for each color channel
                red_error = old_pixel[0] - new_pixel[0]
                green_error = old_pixel[1] - new_pixel[1]
                blue_error = old_pixel[2] - new_pixel[2]

                # Distribute the error to neighboring pixels (Floyd-Steinberg distribution)
                self.distribute_error(x, y, red_error, green_error, blue_error)

    def distribute_error(self, x, y, red_error, green_error, blue_error):
        directions = [
            (1, 0, 7 / 16),   # Right
            (-1, 1, 3 / 16),  # Bottom-left
            (0, 1, 5 / 16),   # Bottom
            (1, 1, 1 / 16)    # Bottom-right
        ]
        for dx, dy, factor in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbor_idx = ny * self.width + nx
                neighbor_pixel = self.image[neighbor_idx]

                # Apply the error distribution
                new_red = min(max(neighbor_pixel[0] + int(red_error * factor), 0), 255)
                new_green = min(max(neighbor_pixel[1] + int(green_error * factor), 0), 255)
                new_blue = min(max(neighbor_pixel[2] + int(blue_error * factor), 0), 255)

                self.image[neighbor_idx] = (new_red, new_green, new_blue)


# Run the dithering on "input.ppm" and save as "output.ppm"
dither = Dither("input.ppm", "output.ppm")
