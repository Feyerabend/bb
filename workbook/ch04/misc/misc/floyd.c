#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int r, g, b;
} Pixel;

Pixel **read_ppm(const char *filename, int *width, int *height, int *max_color_value) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error opening file\n");
        exit(1);
    }

    char header[3];
    fscanf(file, "%2s", header);
    if (header[0] != 'P' || header[1] != '3') {
        fprintf(stderr, "Not a valid PPM file\n");
        fclose(file);
        exit(1);
    }

    fscanf(file, "%d %d %d", width, height, max_color_value);

    Pixel **image = malloc(*height * sizeof(Pixel *));
    for (int i = 0; i < *height; i++) {
        image[i] = malloc(*width * sizeof(Pixel));
        for (int j = 0; j < *width; j++) {
            fscanf(file, "%d %d %d", &image[i][j].r, &image[i][j].g, &image[i][j].b);
        }
    }

    fclose(file);
    return image;
}

void write_ppm(const char *filename, Pixel **image, int width, int height, int max_color_value) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "Error opening file\n");
        exit(1);
    }

    fprintf(file, "P3\n%d %d\n%d\n", width, height, max_color_value);

    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            fprintf(file, "%d %d %d ", image[i][j].r, image[i][j].g, image[i][j].b);
        }
        fprintf(file, "\n");
    }

    fclose(file);
}

void floyd_steinberg_dithering(Pixel **image, int width, int height) {
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            Pixel old_pixel = image[y][x];
            Pixel new_pixel = {
                .r = old_pixel.r < 128 ? 0 : 255,
                .g = old_pixel.g < 128 ? 0 : 255,
                .b = old_pixel.b < 128 ? 0 : 255
            };

            int error_r = old_pixel.r - new_pixel.r;
            int error_g = old_pixel.g - new_pixel.g;
            int error_b = old_pixel.b - new_pixel.b;

            image[y][x] = new_pixel;

            if (x + 1 < width) {
                image[y][x + 1].r += error_r * 7 / 16;
                image[y][x + 1].g += error_g * 7 / 16;
                image[y][x + 1].b += error_b * 7 / 16;
            }
            if (x - 1 >= 0 && y + 1 < height) {
                image[y + 1][x - 1].r += error_r * 3 / 16;
                image[y + 1][x - 1].g += error_g * 3 / 16;
                image[y + 1][x - 1].b += error_b * 3 / 16;
            }
            if (y + 1 < height) {
                image[y + 1][x].r += error_r * 5 / 16;
                image[y + 1][x].g += error_g * 5 / 16;
                image[y + 1][x].b += error_b * 5 / 16;
            }
            if (x + 1 < width && y + 1 < height) {
                image[y + 1][x + 1].r += error_r * 1 / 16;
                image[y + 1][x + 1].g += error_g * 1 / 16;
                image[y + 1][x + 1].b += error_b * 1 / 16;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s input.ppm output.ppm\n", argv[0]);
        return 1;
    }

    int width, height, max_color_value;
    Pixel **image = read_ppm(argv[1], &width, &height, &max_color_value);

    floyd_steinberg_dithering(image, width, height);

    write_ppm(argv[2], image, width, height, max_color_value);

    for (int i = 0; i < height; i++) {
        free(image[i]);
    }
    free(image);

    return 0;
}