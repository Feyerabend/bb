
void transpose(int matrix[3][3], int result[3][3]) {
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            result[j][i] = matrix[i][j];
        }
    }
}

void transpose_opt(int matrix[3][3], int result[3][3]) {
    for (int j = 0; j < 3; j++) {  // swapped loop order for better cache performance
        for (int i = 0; i < 3; i++) {
            result[j][i] = matrix[i][j];
        }
    }
}
