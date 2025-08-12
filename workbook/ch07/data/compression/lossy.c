#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define BLOCK_SIZE 8
#define PI 3.14159265358979323846

// simple 8x8 DCT implementation (similar to JPEG)
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

// Simple quantization matrix (similar to JPEG)
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

void quantize(double dct[BLOCK_SIZE][BLOCK_SIZE], int quantized[BLOCK_SIZE][BLOCK_SIZE], int quality) {
    // Quality factor: 1 = highest compression (lowest quality), 100 = lowest compression (highest quality)
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            int scale_factor = quantization_matrix[i][j] * (100 - quality + 1) / 100;
            if (scale_factor < 1) scale_factor = 1;
            quantized[i][j] = (int)round(dct[i][j] / scale_factor);
        }
    }
}

void dequantize(int quantized[BLOCK_SIZE][BLOCK_SIZE], double dct[BLOCK_SIZE][BLOCK_SIZE], int quality) {
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            int scale_factor = quantization_matrix[i][j] * (100 - quality + 1) / 100;
            if (scale_factor < 1) scale_factor = 1;
            dct[i][j] = quantized[i][j] * scale_factor;
        }
    }
}

// Simple test pattern generator
void generate_test_image(double image[BLOCK_SIZE][BLOCK_SIZE]) {
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            // Create a simple gradient pattern
            image[i][j] = 128 + 64 * sin(i * PI / 4) * cos(j * PI / 4);
        }
    }
}

void print_block(double block[BLOCK_SIZE][BLOCK_SIZE], const char* title) {
    printf("%s:\n", title);
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            printf("%6.1f ", block[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

void print_int_block(int block[BLOCK_SIZE][BLOCK_SIZE], const char* title) {
    printf("%s:\n", title);
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            printf("%4d ", block[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

double calculate_mse(double original[BLOCK_SIZE][BLOCK_SIZE], double compressed[BLOCK_SIZE][BLOCK_SIZE]) {
    double mse = 0.0;
    for (int i = 0; i < BLOCK_SIZE; i++) {
        for (int j = 0; j < BLOCK_SIZE; j++) {
            double diff = original[i][j] - compressed[i][j];
            mse += diff * diff;
        }
    }
    return mse / (BLOCK_SIZE * BLOCK_SIZE);
}

int main() {
    double original[BLOCK_SIZE][BLOCK_SIZE];
    double dct_coeffs[BLOCK_SIZE][BLOCK_SIZE];
    int quantized[BLOCK_SIZE][BLOCK_SIZE];
    double dequantized_dct[BLOCK_SIZE][BLOCK_SIZE];
    double reconstructed[BLOCK_SIZE][BLOCK_SIZE];
    
    // generate test image
    generate_test_image(original);
    print_block(original, "Original 8x8 Block");
    
    // test with different quality levels
    int qualities[] = {10, 50, 90};
    int num_qualities = sizeof(qualities) / sizeof(qualities[0]);
    
    for (int q = 0; q < num_qualities; q++) {
        int quality = qualities[q];
        printf("=== Quality Level: %d ===\n", quality);
        
        // forward DCT
        dct_2d(original, dct_coeffs);
        
        // Qquantization (lossy step)
        quantize(dct_coeffs, quantized, quality);
        print_int_block(quantized, "Quantized DCT Coefficients");
        
        // dequantization
        dequantize(quantized, dequantized_dct, quality);
        
        // inverse DCT
        idct_2d(dequantized_dct, reconstructed);
        print_block(reconstructed, "Reconstructed Block");
        
        // calculate compression metrics
        double mse = calculate_mse(original, reconstructed);
        double psnr = 20 * log10(255.0 / sqrt(mse));
        
        // count non-zero coefficients (rough compression estimate)
        int nonzero_coeffs = 0;
        for (int i = 0; i < BLOCK_SIZE; i++) {
            for (int j = 0; j < BLOCK_SIZE; j++) {
                if (quantized[i][j] != 0) nonzero_coeffs++;
            }
        }
        
        printf("Mean Squared Error: %.2f\n", mse);
        printf("PSNR: %.2f dB\n", psnr);
        printf("Non-zero coefficients: %d/%d (%.1f%%)\n", 
               nonzero_coeffs, BLOCK_SIZE * BLOCK_SIZE, 
               (float)nonzero_coeffs / (BLOCK_SIZE * BLOCK_SIZE) * 100);
        printf("Estimated compression ratio: %.2f:1\n\n", 
               (float)(BLOCK_SIZE * BLOCK_SIZE) / nonzero_coeffs);
    }
    
    return 0;
}

