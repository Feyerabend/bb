#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_TREE_HT 100

struct MinHeapNode {
    char data;
    unsigned freq;
    struct MinHeapNode *left, *right;
};

struct MinHeap {
    unsigned size;
    unsigned capacity;
    struct MinHeapNode** array;
};

struct MinHeapNode* newNode(char data, unsigned freq) {
    struct MinHeapNode* temp = (struct MinHeapNode*)malloc(sizeof(struct MinHeapNode));
    temp->left = temp->right = NULL;
    temp->data = data;
    temp->freq = freq;
    return temp;
}

struct MinHeap* createMinHeap(unsigned capacity) {
    struct MinHeap* minHeap = (struct MinHeap*)malloc(sizeof(struct MinHeap));
    minHeap->size = 0;
    minHeap->capacity = capacity;
    minHeap->array = (struct MinHeapNode**)malloc(minHeap->capacity * sizeof(struct MinHeapNode*));
    return minHeap;
}

void swapMinHeapNode(struct MinHeapNode** a, struct MinHeapNode** b) {
    struct MinHeapNode* t = *a;
    *a = *b;
    *b = t;
}

void minHeapify(struct MinHeap* minHeap, int idx) {
    int smallest = idx;
    int left = 2 * idx + 1;
    int right = 2 * idx + 2;

    if (left < minHeap->size && minHeap->array[left]->freq < minHeap->array[smallest]->freq)
        smallest = left;

    if (right < minHeap->size && minHeap->array[right]->freq < minHeap->array[smallest]->freq)
        smallest = right;

    if (smallest != idx) {
        swapMinHeapNode(&minHeap->array[smallest], &minHeap->array[idx]);
        minHeapify(minHeap, smallest);
    }
}

int isSizeOne(struct MinHeap* minHeap) {
    return (minHeap->size == 1);
}

struct MinHeapNode* extractMin(struct MinHeap* minHeap) {
    struct MinHeapNode* temp = minHeap->array[0];
    minHeap->array[0] = minHeap->array[minHeap->size - 1];
    --minHeap->size;
    minHeapify(minHeap, 0);
    return temp;
}

void insertMinHeap(struct MinHeap* minHeap, struct MinHeapNode* minHeapNode) {
    ++minHeap->size;
    int i = minHeap->size - 1;
    while (i && minHeapNode->freq < minHeap->array[(i - 1) / 2]->freq) {
        minHeap->array[i] = minHeap->array[(i - 1) / 2];
        i = (i - 1) / 2;
    }
    minHeap->array[i] = minHeapNode;
}

void buildMinHeap(struct MinHeap* minHeap) {
    int n = minHeap->size - 1;
    int i;
    for (i = (n - 1) / 2; i >= 0; --i)
        minHeapify(minHeap, i);
}

int isLeaf(struct MinHeapNode* root) {
    return !(root->left) && !(root->right);
}

struct MinHeap* createAndBuildMinHeap(char data[], int freq[], int size) {
    struct MinHeap* minHeap = createMinHeap(size);
    for (int i = 0; i < size; ++i)
        minHeap->array[i] = newNode(data[i], freq[i]);
    minHeap->size = size;
    buildMinHeap(minHeap);
    return minHeap;
}

struct MinHeapNode* buildHuffmanTree(char data[], int freq[], int size) {
    struct MinHeapNode *left, *right, *top;
    struct MinHeap* minHeap = createAndBuildMinHeap(data, freq, size);

    while (!isSizeOne(minHeap)) {
        left = extractMin(minHeap);
        right = extractMin(minHeap);
        top = newNode('$', left->freq + right->freq);
        top->left = left;
        top->right = right;
        insertMinHeap(minHeap, top);
    }
    return extractMin(minHeap);
}

void writeCodesToFile(struct MinHeapNode* root, int arr[], int top, FILE *fp) {
    if (root->left) {
        arr[top] = 0;
        writeCodesToFile(root->left, arr, top + 1, fp);
    }
    if (root->right) {
        arr[top] = 1;
        writeCodesToFile(root->right, arr, top + 1, fp);
    }
    if (isLeaf(root)) {
        fprintf(fp, "%c:", root->data);
        for (int i = 0; i < top; i++) {
            fprintf(fp, "%d", arr[i]);
        }
        fprintf(fp, "\n");
    }
}

void buildHuffmanCodes(struct MinHeapNode* root, int arr[], int top, int codes[256][MAX_TREE_HT], int codeLengths[256]) {
    if (root->left) {
        arr[top] = 0;
        buildHuffmanCodes(root->left, arr, top + 1, codes, codeLengths);
    }
    if (root->right) {
        arr[top] = 1;
        buildHuffmanCodes(root->right, arr, top + 1, codes, codeLengths);
    }
    if (isLeaf(root)) {
        for (int i = 0; i < top; i++) {
            codes[(unsigned char)root->data][i] = arr[i];
        }
        codeLengths[(unsigned char)root->data] = top;
    }
}

void writeBit(int bit, unsigned char *buffer, int *bitPosition, FILE *fp, int *totalBits) {
    if (*bitPosition == 8) {
        fwrite(buffer, 1, 1, fp);
        *buffer = 0;
        *bitPosition = 0;
    }
    *buffer |= (bit << (7 - *bitPosition));
    (*bitPosition)++;
    (*totalBits)++;
}

void encodeText(FILE *input, FILE *output, int codes[256][MAX_TREE_HT], int codeLengths[256], int *totalBits) {
    unsigned char buffer = 0;
    int bitPosition = 0;
    char ch;
    while ((ch = fgetc(input)) != EOF) {
        for (int i = 0; i < codeLengths[(unsigned char)ch]; i++) {
            writeBit(codes[(unsigned char)ch][i], &buffer, &bitPosition, output, totalBits);
        }
    }
    if (bitPosition > 0) {
        fwrite(&buffer, 1, 1, output);
    }
}

int readBit(unsigned char *buffer, int *bitPosition, FILE *fp) {
    if (*bitPosition == 8) {
        fread(buffer, 1, 1, fp);
        *bitPosition = 0;
    }
    int bit = (*buffer >> (7 - *bitPosition)) & 1;
    (*bitPosition)++;
    return bit;
}

void decodeText(FILE *input, FILE *output, struct MinHeapNode* root, int totalBits) {
    unsigned char buffer = 0;
    int bitPosition = 8;
    struct MinHeapNode* current = root;
    int bitsRead = 0;

    while (bitsRead < totalBits) {
        int bit = readBit(&buffer, &bitPosition, input);
        bitsRead++;
        if (bit == 0) {
            current = current->left;
        } else {
            current = current->right;
        }
        if (isLeaf(current)) {
            fputc(current->data, output);
            current = root;
        }
    }
}

int main() {
    char inputFileName[] = "input.txt";
    char compressedFileName[] = "compressed.bin";
    char decompressedFileName[] = "decompressed.txt";

    FILE *inputFile = fopen(inputFileName, "r");
    if (!inputFile) {
        printf("Error opening input file!\n");
        return 1;
    }

    int freq[256] = {0};
    char ch;
    while ((ch = fgetc(inputFile)) != EOF) {
        freq[(unsigned char)ch]++;
    }
    fclose(inputFile);

    char data[256];
    int size = 0;
    for (int i = 0; i < 256; i++) {
        if (freq[i] > 0) {
            data[size++] = (char)i;
        }
    }
    struct MinHeapNode* root = buildHuffmanTree(data, freq, size);

    int codes[256][MAX_TREE_HT];
    int codeLengths[256] = {0};
    int arr[MAX_TREE_HT], top = 0;
    buildHuffmanCodes(root, arr, top, codes, codeLengths);

    FILE *codeFile = fopen("huffman_codes.txt", "w");
    if (!codeFile) {
        printf("Error opening code file!\n");
        return 1;
    }
    writeCodesToFile(root, arr, top, codeFile);
    fclose(codeFile);

    inputFile = fopen(inputFileName, "r");
    FILE *compressedFile = fopen(compressedFileName, "wb");
    if (!inputFile || !compressedFile) {
        printf("Error opening files for encoding!\n");
        return 1;
    }
    int totalBits = 0;
    encodeText(inputFile, compressedFile, codes, codeLengths, &totalBits);
    fclose(inputFile);
    fclose(compressedFile);

    FILE *compressedFileRead = fopen(compressedFileName, "rb");
    FILE *decompressedFile = fopen(decompressedFileName, "w");
    if (!compressedFileRead || !decompressedFile) {
        printf("Error opening files for decoding!\n");
        return 1;
    }
    decodeText(compressedFileRead, decompressedFile, root, totalBits);
    fclose(compressedFileRead);
    fclose(decompressedFile);

    printf("Compression and decompression completed successfully!\n");
    return 0;
}