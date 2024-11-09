import unittest
import os
from output_buffer import OutputBuffer

class TestOutputBuffer(unittest.TestCase):

    def setUp(self):
        """Create an OutputBuffer object before each test."""
        self.buffer = OutputBuffer(100, 100)

    def test_draw_and_save_image(self):
        """Test drawing on an image and saving it to a folder."""
        # Create a new OutputBuffer with a larger size for more drawing space
        buffer = OutputBuffer(200, 200)
        
        # Draw a rectangle from (50, 50) to (150, 150)
        buffer.draw_rectangle(50, 50, 150, 150, (0, 255, 0))  # Green rectangle
        
        # Ensure the folder exists, create if it doesn't
        output_folder = 'output_images'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Save the image to the folder
        filename = os.path.join(output_folder, 'test_image_with_rectangle.png')
        buffer.save(filename)
        
        # Assert the image file exists
        self.assertTrue(os.path.exists(filename))
        
        # Show the image after saving (for debugging purposes)
        buffer.image.show()  # This will pop up a window displaying the image

        # Cleanup - remove the saved file after test
        #os.remove(filename)

if __name__ == "__main__":
    unittest.main()
