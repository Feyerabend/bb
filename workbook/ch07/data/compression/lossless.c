#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WINDOW_SIZE 4096
#define LOOKAHEAD_SIZE 18
#define MIN_MATCH_LENGTH 3

typedef struct {
    int offset;
    int length;
    char next_char;
} Token;

// simple LZ77 implementation
int find_longest_match(const char* data, int pos, int data_len, int* offset, int* length) {
    int best_offset = 0;
    int best_length = 0;
    
    int window_start = (pos > WINDOW_SIZE) ? pos - WINDOW_SIZE : 0;
    int lookahead_end = (pos + LOOKAHEAD_SIZE < data_len) ? pos + LOOKAHEAD_SIZE : data_len;
    
    for (int i = window_start; i < pos; i++) {
        int match_length = 0;
        while (pos + match_length < lookahead_end && 
               data[i + match_length] == data[pos + match_length] &&
               match_length < LOOKAHEAD_SIZE) {
            match_length++;
        }
        
        if (match_length >= MIN_MATCH_LENGTH && match_length > best_length) {
            best_offset = pos - i;
            best_length = match_length;
        }
    }
    
    *offset = best_offset;
    *length = best_length;
    return best_length >= MIN_MATCH_LENGTH;
}

int compress_lz77(const char* input, int input_len, Token* output, int max_tokens) {
    int pos = 0;
    int token_count = 0;
    
    while (pos < input_len && token_count < max_tokens) {
        int offset, length;
        
        if (find_longest_match(input, pos, input_len, &offset, &length)) {
            output[token_count].offset = offset;
            output[token_count].length = length;
            output[token_count].next_char = (pos + length < input_len) ? input[pos + length] : '\0';
            pos += length + 1;
        } else {
            output[token_count].offset = 0;
            output[token_count].length = 0;
            output[token_count].next_char = input[pos];
            pos++;
        }
        token_count++;
    }
    
    return token_count;
}

void decompress_lz77(Token* tokens, int token_count, char* output) {
    int out_pos = 0;
    
    for (int i = 0; i < token_count; i++) {
        if (tokens[i].length > 0) {
            // copy from window
            int copy_start = out_pos - tokens[i].offset;
            for (int j = 0; j < tokens[i].length; j++) {
                output[out_pos++] = output[copy_start + j];
            }
        }
        
        if (tokens[i].next_char != '\0') {
            output[out_pos++] = tokens[i].next_char;
        }
    }
    output[out_pos] = '\0';
}

// run-Length Encoding (simpler lossless compression)
int rle_compress(const char* input, int input_len, char* output) {
    int out_pos = 0;
    int i = 0;
    
    while (i < input_len) {
        char current = input[i];
        int count = 1;
        
        while (i + count < input_len && input[i + count] == current && count < 255) {
            count++;
        }
        
        if (count >= 4) {  // Only use RLE for runs of 4 or more
            // use RLE format: [255 as marker][count][char]
            output[out_pos++] = (char)255;  // Escape marker
            output[out_pos++] = (char)count;
            output[out_pos++] = current;
        } else {
            // direct copy for short runs
            for (int j = 0; j < count; j++) {
                output[out_pos++] = current;
            }
        }
        i += count;
    }
    
    return out_pos;
}

int rle_decompress(const char* input, int input_len, char* output) {
    int out_pos = 0;
    int i = 0;
    
    while (i < input_len) {
        if (i < input_len - 2 && (unsigned char)input[i] == 255) {
            // This is an RLE sequence: [255][count][char]
            int count = (unsigned char)input[i + 1];
            char ch = input[i + 2];
            
            for (int j = 0; j < count; j++) {
                output[out_pos++] = ch;
            }
            i += 3;
        } else {
            // Regular character
            output[out_pos++] = input[i];
            i++;
        }
    }
    
    output[out_pos] = '\0';
    return out_pos;
}

int main() {
    // test data
    const char* test_data = "AAABBBCCCDDDAAABBBCCCDDDAAABBBCCCDDD Hello World! This is a test string for compression algorithms.";
    int data_len = strlen(test_data);
    
    printf("Original data: %s\n", test_data);
    printf("Original length: %d bytes\n\n", data_len);
    
    // test RLE compression
    char rle_compressed[1000];
    int rle_comp_len = rle_compress(test_data, data_len, rle_compressed);
    
    char rle_decompressed[1000];
    int rle_decomp_len = rle_decompress(rle_compressed, rle_comp_len, rle_decompressed);
    
    printf("=== RLE Compression ===\n");
    printf("Compressed length: %d bytes\n", rle_comp_len);
    printf("Compression ratio: %.2f%%\n", (float)rle_comp_len / data_len * 100);
    printf("Decompressed: %s\n", rle_decompressed);
    printf("Match original: %s\n\n", strcmp(test_data, rle_decompressed) == 0 ? "YES" : "NO");
    
    // test LZ77 compression
    Token lz77_compressed[1000];
    int token_count = compress_lz77(test_data, data_len, lz77_compressed, 1000);
    
    char lz77_decompressed[1000];
    decompress_lz77(lz77_compressed, token_count, lz77_decompressed);
    
    printf("=== LZ77 Compression ===\n");
    printf("Token count: %d\n", token_count);
    printf("Estimated compressed size: %zu bytes\n", token_count * sizeof(Token));
    printf("Decompressed: %s\n", lz77_decompressed);
    printf("Match original: %s\n", strcmp(test_data, lz77_decompressed) == 0 ? "YES" : "NO");
    
    return 0;
}

