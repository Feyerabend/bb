# converter.py

from ppm_reader import read_ppm
from gif_writer import write_gif

def convert_ppm_to_gif(ppm_filename, gif_filename):
    width, height, image = read_ppm(ppm_filename)
    write_gif(gif_filename, width, height, image)
    print(f"Converted {ppm_filename} to {gif_filename}")

# Example usage
if __name__ == "__main__":
    convert_ppm_to_gif('output.ppm', 'output.gif')