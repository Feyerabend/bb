// gcc -o lossyppm lossyppm.c -lm

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define BLOCK_SIZE 8
#define PI 3.14159265358979323846
#define MAX_WIDTH 2048
#define MAX_HEIGHT 2048
#define MAX_COEFFS 1000000

typedef struct {
    int width;
    int height;
    int max_val;
    unsigned char *r, *g, *b;
} PPMImage;

typedef struct {
    short value;
    unsigned char run_length;
} RLEEntry;

typedef struct {
    int width, height, max_val, quality;
    int num_blocks_x, num_blocks_y;
    int r_size, g_size, b_size;
    RLEEntry *r_data, *g_data, *b_data;
} CompressedImage;

// DCT functions
void dct_2d(double input[BLOCK_SIZE][BLOCK_SIZE], double output[BLOCK_SIZE][BLOCK_SIZE]) {
    for (int u = 0; u < BLOCK_SIZE; u++) {
        for (int v = 0; v < BLOCK_SIZE; v++) {
            double sum = 0.0;
            double cu = (u == 0) ? 1.0/sqrt(2.0) : 1.0;
            double cv = (v == 0) ? 1.0/sqrt(2.0) : 1.0;
            
            for (int x = 0; x < BLOCK_SIZE; x++) {
                for (int y = 0; y < BLOCK_SIZE; y++) {
                    double cos_u = cos((2*x + 1) * u * PI / (2.0 * BLOCK_SIZE));
                    double cos_v = cos((2*y + 1) * v * PI / (2.0 * BLOCK_SIZE));
                    sum += input[x][y] * cos_u * cos_v;
                }
            }
            
            output[u][v] = 0.25 * cu * cv * sum;
        }
    }
}

void idct_2d(double input[BLOCK_SIZE][BLOCK_SIZE], double output[BLOCK_SIZE][BLOCK_SIZE]) {
    for (int x = 0; x < BLOCK_SIZE; x++) {
        for (int y = 0; y < BLOCK_SIZE; y++) {
            double sum = 0.0;
            
            for (int u = 0; u < BLOCK_SIZE; u++) {
                for (int v = 0; v < BLOCK_SIZE; v++) {
                    double cu = (u == 0) ? 1.0/sqrt(2.0) : 1.0;
                    double cv = (v == 0) ? 1.0/sqrt(2.0) : 1.0;
                    double cos_u = cos((2*x + 1) * u * PI / (2.0 * BLOCK_SIZE));
                    double cos_v = cos((2*y + 1) * v * PI / (2.0 * BLOCK_SIZE));
                    
                    sum += cu * cv * input[u][v] * cos_u * cos_v;
                }
            }
            
            output[x][y] = 0.25 * sum;
        }
    }
}

int quantization_matrix[BLOCK_SIZE][BLOCK_SIZE] = {
    {16, 11, 10, 16,  24,  40,  51,  61},
    {12, 12, 14, 19,  26,  58,  60,  55},
    {14, 13, 16, 24,  40,  57,  69,  56},
    {14, 17, 22, 29,  51,  87,  80,  62},
    {18, 22, 37, 56,  68, 109, 103,  77},
    {24, 35, 55, 64,  81, 104, 113,  92},
    {49, 64, 78, 87, 103, 121, 120, 101},
    {72, 92, 95, 98, 112, 100, 103,  99}
};

void quantize(double dct[BLOCK_SIZE][BLOCK_SIZE], short quantized[BLOCK_SIZE][BLOCK_SIZE], int quality) {
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            int scale_factor = quantization_matrix[i][j] * (100 - quality + 1) / 100;
            if (scale_factor < 1) scale_factor = 1;
            quantized[i][j] = (short)round(dct[i][j] / scale_factor);
        }
    }
}

void dequantize(short quantized[BLOCK_SIZE][BLOCK_SIZE], double dct[BLOCK_SIZE][BLOCK_SIZE], int quality) {
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            int scale_factor = quantization_matrix[i][j] * (100 - quality + 1) / 100;
            if (scale_factor < 1) scale_factor = 1;
            dct[i][j] = quantized[i][j] * scale_factor;
        }
    }
}

// Zigzag pattern for coefficient ordering (JPEG standard)
int zigzag_order[64][2] = {
    {0,0}, {0,1}, {1,0}, {2,0}, {1,1}, {0,2}, {0,3}, {1,2},
    {2,1}, {3,0}, {4,0}, {3,1}, {2,2}, {1,3}, {0,4}, {0,5},
    {1,4}, {2,3}, {3,2}, {4,1}, {5,0}, {6,0}, {5,1}, {4,2},
    {3,3}, {2,4}, {1,5}, {0,6}, {0,7}, {1,6}, {2,5}, {3,4},
    {4,3}, {5,2}, {6,1}, {7,0}, {7,1}, {6,2}, {5,3}, {4,4},
    {3,5}, {2,6}, {1,7}, {2,7}, {3,6}, {4,5}, {5,4}, {6,3},
    {7,2}, {7,3}, {6,4}, {5,5}, {4,6}, {3,7}, {4,7}, {5,6},
    {6,5}, {7,4}, {7,5}, {6,6}, {5,7}, {6,7}, {7,6}, {7,7}
};

// Convert 8x8 block to zigzag order
void block_to_zigzag(short block[BLOCK_SIZE][BLOCK_SIZE], short zigzag[64]) {
    for (int i = 0; i < 64; i++) {
        int row = zigzag_order[i][0];
        int col = zigzag_order[i][1];
        zigzag[i] = block[row][col];
    }
}

void zigzag_to_block(short zigzag[64], short block[BLOCK_SIZE][BLOCK_SIZE]) {
    for (int i = 0; i < 64; i++) {
        int row = zigzag_order[i][0];
        int col = zigzag_order[i][1];
        block[row][col] = zigzag[i];
    }
}

// Run-length encoding for zigzag coefficients
int run_length_encode(short *coeffs, int count, RLEEntry *output, int max_output) {
    int output_idx = 0;
    int i = 0;
    
    while (i < count && output_idx < max_output - 1) {
        if (coeffs[i] == 0) {
            // Count consecutive zeros
            int run = 0;
            while (i < count && coeffs[i] == 0 && run < 255) {
                run++;
                i++;
            }
            output[output_idx].value = 0;
            output[output_idx].run_length = run;
            output_idx++;
        } else {
            // Non-zero coefficient
            output[output_idx].value = coeffs[i];
            output[output_idx].run_length = 1;
            output_idx++;
            i++;
        }
    }
    
    return output_idx;
}

// Run-length decoding
void run_length_decode(RLEEntry *input, int input_size, short *output, int max_output) {
    int output_idx = 0;
    
    for (int i = 0; i < input_size && output_idx < max_output; i++) {
        for (int j = 0; j < input[i].run_length && output_idx < max_output; j++) {
            output[output_idx++] = input[i].value;
        }
    }
}

// PPM I/O functions
PPMImage* read_ppm(const char* filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        printf("Error: Cannot open file %s\n", filename);
        return NULL;
    }
    
    PPMImage *img = malloc(sizeof(PPMImage));
    if (!img) {
        fclose(fp);
        return NULL;
    }
    
    char magic[3];
    if (fscanf(fp, "%2s", magic) != 1 || strcmp(magic, "P3") != 0) {
        printf("Error: Not a valid P3 PPM file\n");
        free(img);
        fclose(fp);
        return NULL;
    }
    
    // Skip comments and whitespace
    int c;
    while ((c = fgetc(fp)) != EOF) {
        if (c == '#') {
            while ((c = fgetc(fp)) != EOF && c != '\n');
        } else if (c != ' ' && c != '\t' && c != '\n' && c != '\r') {
            ungetc(c, fp);
            break;
        }
    }
    
    if (fscanf(fp, "%d %d %d", &img->width, &img->height, &img->max_val) != 3) {
        printf("Error: Could not read image header\n");
        free(img);
        fclose(fp);
        return NULL;
    }
    
    if (img->width <= 0 || img->height <= 0) {
        printf("Error: Invalid dimensions\n");
        free(img);
        fclose(fp);
        return NULL;
    }
    
    int size = img->width * img->height;
    img->r = malloc(size);
    img->g = malloc(size);
    img->b = malloc(size);
    
    if (!img->r || !img->g || !img->b) {
        free(img->r); free(img->g); free(img->b); free(img);
        fclose(fp);
        return NULL;
    }
    
    for (int i = 0; i < size; i++) {
        int r, g, b;
        if (fscanf(fp, "%d %d %d", &r, &g, &b) != 3) {
            printf("Error reading pixel data\n");
            free(img->r); free(img->g); free(img->b); free(img);
            fclose(fp);
            return NULL;
        }
        img->r[i] = (unsigned char)r;
        img->g[i] = (unsigned char)g;
        img->b[i] = (unsigned char)b;
    }
    
    fclose(fp);
    printf("Read image: %dx%d\n", img->width, img->height);
    return img;
}

unsigned char clamp(double value) {
    if (value < 0) return 0;
    if (value > 255) return 255;
    return (unsigned char)round(value);
}

// Compress image to custom format with actual size reduction
CompressedImage* compress_to_format(PPMImage *img, int quality) {
    if (!img) return NULL;
    
    CompressedImage *compressed = malloc(sizeof(CompressedImage));
    if (!compressed) return NULL;
    
    compressed->width = img->width;
    compressed->height = img->height;
    compressed->max_val = img->max_val;
    compressed->quality = quality;
    compressed->num_blocks_x = (img->width + BLOCK_SIZE - 1) / BLOCK_SIZE;
    compressed->num_blocks_y = (img->height + BLOCK_SIZE - 1) / BLOCK_SIZE;
    
    int total_blocks = compressed->num_blocks_x * compressed->num_blocks_y;
    
    // Allocate temporary arrays for all coefficients
    short *temp_coeffs = malloc(total_blocks * 64 * sizeof(short));
    RLEEntry *temp_rle = malloc(total_blocks * 64 * sizeof(RLEEntry));
    
    if (!temp_coeffs || !temp_rle) {
        free(compressed);
        free(temp_coeffs);
        free(temp_rle);
        return NULL;
    }
    
    // Process each color channel
    unsigned char *channels[3] = {img->r, img->g, img->b};
    RLEEntry **channel_data[3] = {&compressed->r_data, &compressed->g_data, &compressed->b_data};
    int *channel_sizes[3] = {&compressed->r_size, &compressed->g_size, &compressed->b_size};
    
    for (int ch = 0; ch < 3; ch++) {
        int coeff_count = 0;
        
        // Process all blocks for this channel
        for (int block_y = 0; block_y < compressed->num_blocks_y; block_y++) {
            for (int block_x = 0; block_x < compressed->num_blocks_x; block_x++) {
                double input[BLOCK_SIZE][BLOCK_SIZE];
                double dct_coeffs[BLOCK_SIZE][BLOCK_SIZE];
                short quantized[BLOCK_SIZE][BLOCK_SIZE];
                short zigzag[64];
                
                // Extract 8x8 block
                for (int i = 0; i < BLOCK_SIZE; i++) {
                    for (int j = 0; j < BLOCK_SIZE; j++) {
                        int x = block_y * BLOCK_SIZE + i;
                        int y = block_x * BLOCK_SIZE + j;
                        
                        if (x >= img->height) x = img->height - 1;
                        if (y >= img->width) y = img->width - 1;
                        
                        input[i][j] = channels[ch][x * img->width + y] - 128.0;
                    }
                }
                
                // DCT + Quantization + Zigzag
                dct_2d(input, dct_coeffs);
                quantize(dct_coeffs, quantized, quality);
                block_to_zigzag(quantized, zigzag);
                
                // Store coefficients
                for (int i = 0; i < 64; i++) {
                    temp_coeffs[coeff_count++] = zigzag[i];
                }
            }
        }
        
        // Run-length encode all coefficients for this channel
        int rle_size = run_length_encode(temp_coeffs, coeff_count, temp_rle, total_blocks * 64);
        
        // Allocate and copy RLE data
        *channel_data[ch] = malloc(rle_size * sizeof(RLEEntry));
        if (*channel_data[ch]) {
            memcpy(*channel_data[ch], temp_rle, rle_size * sizeof(RLEEntry));
            *channel_sizes[ch] = rle_size;
        } else {
            *channel_sizes[ch] = 0;
        }
    }
    
    free(temp_coeffs);
    free(temp_rle);
    return compressed;
}

// Decompress and create PPM
PPMImage* decompress_from_format(CompressedImage *compressed) {
    if (!compressed) return NULL;
    
    PPMImage *img = malloc(sizeof(PPMImage));
    if (!img) return NULL;
    
    img->width = compressed->width;
    img->height = compressed->height;
    img->max_val = compressed->max_val;
    
    int size = img->width * img->height;
    img->r = malloc(size);
    img->g = malloc(size);
    img->b = malloc(size);
    
    if (!img->r || !img->g || !img->b) {
        free(img->r); free(img->g); free(img->b); free(img);
        return NULL;
    }
    
    int total_blocks = compressed->num_blocks_x * compressed->num_blocks_y;
    short *temp_coeffs = malloc(total_blocks * 64 * sizeof(short));
    
    if (!temp_coeffs) {
        free(img->r); free(img->g); free(img->b); free(img);
        return NULL;
    }
    
    // Process each channel
    RLEEntry *channel_data[3] = {compressed->r_data, compressed->g_data, compressed->b_data};
    int channel_sizes[3] = {compressed->r_size, compressed->g_size, compressed->b_size};
    unsigned char *channels[3] = {img->r, img->g, img->b};
    
    for (int ch = 0; ch < 3; ch++) {
        // Decode RLE
        run_length_decode(channel_data[ch], channel_sizes[ch], temp_coeffs, total_blocks * 64);
        
        int coeff_idx = 0;
        
        // Process blocks
        for (int block_y = 0; block_y < compressed->num_blocks_y; block_y++) {
            for (int block_x = 0; block_x < compressed->num_blocks_x; block_x++) {
                short zigzag[64];
                short quantized[BLOCK_SIZE][BLOCK_SIZE];
                double dct_coeffs[BLOCK_SIZE][BLOCK_SIZE];
                double output[BLOCK_SIZE][BLOCK_SIZE];
                
                // Get coefficients for this block
                for (int i = 0; i < 64; i++) {
                    zigzag[i] = temp_coeffs[coeff_idx++];
                }
                
                // Reconstruct block
                zigzag_to_block(zigzag, quantized);
                dequantize(quantized, dct_coeffs, compressed->quality);
                idct_2d(dct_coeffs, output);
                
                // Write back to image
                for (int i = 0; i < BLOCK_SIZE; i++) {
                    for (int j = 0; j < BLOCK_SIZE; j++) {
                        int x = block_y * BLOCK_SIZE + i;
                        int y = block_x * BLOCK_SIZE + j;
                        
                        if (x < img->height && y < img->width) {
                            channels[ch][x * img->width + y] = clamp(output[i][j] + 128.0);
                        }
                    }
                }
            }
        }
    }
    
    free(temp_coeffs);
    return img;
}

// Save compressed format to binary file
int save_compressed(const char *filename, CompressedImage *compressed) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) return 0;
    
    // Write header
    fwrite(&compressed->width, sizeof(int), 1, fp);
    fwrite(&compressed->height, sizeof(int), 1, fp);
    fwrite(&compressed->max_val, sizeof(int), 1, fp);
    fwrite(&compressed->quality, sizeof(int), 1, fp);
    fwrite(&compressed->num_blocks_x, sizeof(int), 1, fp);
    fwrite(&compressed->num_blocks_y, sizeof(int), 1, fp);
    
    // Write channel data
    fwrite(&compressed->r_size, sizeof(int), 1, fp);
    fwrite(compressed->r_data, sizeof(RLEEntry), compressed->r_size, fp);
    
    fwrite(&compressed->g_size, sizeof(int), 1, fp);
    fwrite(compressed->g_data, sizeof(RLEEntry), compressed->g_size, fp);
    
    fwrite(&compressed->b_size, sizeof(int), 1, fp);
    fwrite(compressed->b_data, sizeof(RLEEntry), compressed->b_size, fp);
    
    fclose(fp);
    return 1;
}

void free_compressed(CompressedImage *compressed) {
    if (compressed) {
        free(compressed->r_data);
        free(compressed->g_data);
        free(compressed->b_data);
        free(compressed);
    }
}

int write_ppm(const char* filename, PPMImage *img) {
    FILE *fp = fopen(filename, "w");
    if (!fp) return 0;
    
    fprintf(fp, "P3\n%d %d\n%d\n", img->width, img->height, img->max_val);
    for (int i = 0; i < img->width * img->height; i++) {
        fprintf(fp, "%d %d %d\n", img->r[i], img->g[i], img->b[i]);
    }
    
    fclose(fp);
    return 1;
}

void free_ppm(PPMImage *img) {
    if (img) {
        free(img->r); free(img->g); free(img->b); free(img);
    }
}

double calculate_compression_ratio(const char *original_file, const char *compressed_file) {
    FILE *f1 = fopen(original_file, "r");
    FILE *f2 = fopen(compressed_file, "rb");
    
    if (!f1 || !f2) {
        if (f1) fclose(f1);
        if (f2) fclose(f2);
        return 0.0;
    }
    
    fseek(f1, 0, SEEK_END);
    long size1 = ftell(f1);
    fseek(f2, 0, SEEK_END);
    long size2 = ftell(f2);
    
    fclose(f1);
    fclose(f2);
    
    return (double)size1 / size2;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <input.ppm>\n", argv[0]);
        return 1;
    }
    
    PPMImage *original = read_ppm(argv[1]);
    if (!original) return 1;
    
    int qualities[] = {10, 30, 50, 70, 90};
    int num_qualities = sizeof(qualities) / sizeof(qualities[0]);
    
    printf("\nCompression Results:\n");
    printf("Quality | Comp Ratio | File Size | Compressed File\n");
    printf("--------|------------|-----------|----------------\n");
    
    for (int i = 0; i < num_qualities; i++) {
        int quality = qualities[i];
        
        // Compress to custom format
        CompressedImage *compressed = compress_to_format(original, quality);
        if (!compressed) continue;
        
        // Save compressed format
        char comp_filename[256];
        snprintf(comp_filename, sizeof(comp_filename), "compressed_q%d.dct", quality);
        
        if (save_compressed(comp_filename, compressed)) {
            double ratio = calculate_compression_ratio(argv[1], comp_filename);
            
            FILE *fp = fopen(comp_filename, "rb");
            fseek(fp, 0, SEEK_END);
            long comp_size = ftell(fp);
            fclose(fp);
            
            printf("   %2d   |    %5.2fx   |   %6ld  | %s\n", 
                   quality, ratio, comp_size, comp_filename);
            
            // Also create decompressed PPM for viewing
            PPMImage *decompressed = decompress_from_format(compressed);
            if (decompressed) {
                char ppm_filename[256];
                snprintf(ppm_filename, sizeof(ppm_filename), "decompressed_q%d.ppm", quality);
                write_ppm(ppm_filename, decompressed);
                free_ppm(decompressed);
            }
        }
        
        free_compressed(compressed);
    }
    
    printf("\nFiles created:\n");
    printf("- *.dct files: Compressed binary format (actual size reduction)\n");
    printf("- decompressed_*.ppm files: For viewing quality differences\n");
    
    free_ppm(original);
    return 0;
}

