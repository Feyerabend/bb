# ppm.py
def save_ppm(filename, width, height, pixel_data):
    with open(filename, 'w') as f:
        f.write(f'P3\n{width} {height}\n255\n')
        for row in pixel_data:
            f.write(' '.join(' '.join(map(str, pixel)) for pixel in row) + '\n')