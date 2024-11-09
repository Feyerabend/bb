import unittest
import os
import random
from output_buffer import OutputBuffer


class TestOutputBuffer(unittest.TestCase):

    def setUp(self):
        """Create an OutputBuffer object before each test."""
        self.buffer = OutputBuffer(100, 100)  # 100x100 image buffer
        self.buffer.set_pixel(50, 50, (255, 0, 0))  # Set a red pixel in the middle

    def test_save_ppm(self):
        """Test saving the image as a PPM file."""
        filename = 'output_images/test_image.ppm'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')
        
        self.buffer.save(filename, "ppm")
        
        # Assert that the PPM file is created
        self.assertTrue(os.path.exists(filename))

        # Check if the PPM file starts with the correct header
        with open(filename, 'r') as f:
            header = f.readline()
            self.assertEqual(header.strip(), "P3")  # Check PPM header
        # Keep the file for inspection
        # os.remove(filename)

    def test_save_png(self):
        """Test saving the image as a PNG file."""
        filename = 'output_images/test_image.png'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')
        
        self.buffer.save(filename, "png")

        # Assert that the PNG file is created
        self.assertTrue(os.path.exists(filename))

        # Keep the file for inspection
        # os.remove(filename)

    def test_save_jpeg(self):
        """Test saving the image as a JPEG file."""
        filename = 'output_images/test_image.jpeg'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')

        self.buffer.save(filename, "jpeg")

        # Assert that the JPEG file is created
        self.assertTrue(os.path.exists(filename))

        # Keep the file for inspection
        # os.remove(filename)

    def test_save_bmp(self):
        """Test saving the image as a BMP file."""
        filename = 'output_images/test_image.bmp'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')

        self.buffer.save(filename, "bmp")

        # Assert that the BMP file is created
        self.assertTrue(os.path.exists(filename))

        # Keep the file for inspection
        # os.remove(filename)

    def test_save_tiff(self):
        """Test saving the image as a TIFF file."""
        filename = 'output_images/test_image.tiff'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')

        self.buffer.save(filename, "tiff")

        # Assert that the TIFF file is created
        self.assertTrue(os.path.exists(filename))

        # Keep the file for inspection
        # os.remove(filename)

    # New Tests for Gradient and Random Color Fill

    def test_gradient_fill(self):
        """Test generating a gradient image."""
        filename = 'output_images/test_gradient.png'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')

        width, height = self.buffer.width, self.buffer.height
        for y in range(height):
            for x in range(width):
                # Simple gradient fill from black to white horizontally
                r = int(x / width * 255)
                g = int(y / height * 255)
                b = 128  # Static blue component
                self.buffer.set_pixel(x, y, (r, g, b))

        self.buffer.save(filename, "png")

        # Assert that the PNG file is created
        self.assertTrue(os.path.exists(filename))
        # Keep the file for inspection
        # os.remove(filename)

    def test_random_fill(self):
        """Test generating a random color image."""
        filename = 'output_images/test_random.png'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')

        for y in range(self.buffer.height):
            for x in range(self.buffer.width):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                self.buffer.set_pixel(x, y, (r, g, b))

        self.buffer.save(filename, "png")

        # Assert that the PNG file is created
        self.assertTrue(os.path.exists(filename))
        # Keep the file for inspection
        # os.remove(filename)

    def test_colored_region(self):
        """Test filling a specific region of the image with a color."""
        filename = 'output_images/test_colored_region.png'
        if not os.path.exists('output_images'):
            os.makedirs('output_images')

        # Fill a rectangular region (from (20, 20) to (80, 80)) with blue color
        for y in range(20, 80):
            for x in range(20, 80):
                self.buffer.set_pixel(x, y, (0, 0, 255))  # Blue

        self.buffer.save(filename, "png")

        # Assert that the PNG file is created
        self.assertTrue(os.path.exists(filename))
        # Keep the file for inspection
        # os.remove(filename)

    def tearDown(self):
        """Clean up after each test."""
        # Commented out to not delete the files
        # if os.path.exists('output_images'):
        #     for f in os.listdir('output_images'):
        #         os.remove(os.path.join('output_images', f))
        #     os.rmdir('output_images')
        pass


if __name__ == "__main__":
    unittest.main()