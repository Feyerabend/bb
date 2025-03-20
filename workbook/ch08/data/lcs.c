#include <stdio.h>
#include <string.h>

void lcs(char *X, char *Y) {
    int m = strlen(X), n = strlen(Y);
    int dp[m + 1][n + 1]; // dyn. prog. tabl.

    for (int i = 0; i <= m; i++) {
        for (int j = 0; j <= n; j++) {
            if (i == 0 || j == 0)
                dp[i][j] = 0;
            else if (X[i - 1] == Y[j - 1])
                dp[i][j] = dp[i - 1][j - 1] + 1;
            else
                dp[i][j] = (dp[i - 1][j] > dp[i][j - 1]) ? dp[i - 1][j] : dp[i][j - 1];
        }
    }

    int i = m, j = n, index = dp[m][n];
    char lcs_str[index + 1];
    lcs_str[index] = '\0';

    while (i > 0 && j > 0) {
        if (X[i - 1] == Y[j - 1]) {
            lcs_str[--index] = X[i - 1];
            i--;
            j--;
        } else if (dp[i - 1][j] > dp[i][j - 1])
            i--;
        else
            j--;
    }

    printf("LCS: %s\n", lcs_str);
}

int main() {
    char X[] = "AGGTAB";
    char Y[] = "GXTXAYB";

    lcs(X, Y);
    return 0;
}
