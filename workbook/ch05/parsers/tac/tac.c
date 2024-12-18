#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#define MAX_LEN 100

// struct: TAC instruction
typedef struct {
    char op;     // operator ('+', '-', '*', '/')
    char result; // temporary variable (t1, t2, etc.)
    char arg1;   // first operand
    char arg2;   // second operand
} TAC;

// generate temporary variable names
char generateTempVar(int tempCount) {
    return 't' + tempCount; // variable names like t1, t2, etc.
}

// tokenise the input string (handle parentheses)
void tokenize(const char *expr, char tokens[MAX_LEN][MAX_LEN], int *tokenCount) {
    int i = 0, j = 0;
    while (expr[i] != '\0') {
        if (isdigit(expr[i]) || isalpha(expr[i])) {
            tokens[*tokenCount][j++] = expr[i++];
            tokens[*tokenCount][j] = '\0';
            (*tokenCount)++;
            j = 0;
        } else if (expr[i] == '+' || expr[i] == '-' || expr[i] == '*' || expr[i] == '/') {
            tokens[*tokenCount][0] = expr[i++];
            tokens[*tokenCount][1] = '\0';
            (*tokenCount)++;
        } else if (expr[i] == '(' || expr[i] == ')') {
            tokens[*tokenCount][0] = expr[i++];
            tokens[*tokenCount][1] = '\0';
            (*tokenCount)++;
        } else if (expr[i] == ' ') {
            i++;  // skip spaces
        } else {
            i++;  // skip other characters
        }
    }
}

// handle precedence
int precedence(char op) {
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    return 0;
}

// convert the tokens into TAC
void parseToTAC(char tokens[MAX_LEN][MAX_LEN], int tokenCount) {
    TAC tac[MAX_LEN];
    int tacCount = 0;
    int tempCount = 0;
    char stack[MAX_LEN];
    int stackTop = -1;

    // loop through each token
    for (int i = 0; i < tokenCount; i++) {
        char *token = tokens[i];
        
        if (isdigit(token[0]) || isalpha(token[0])) {
            // operand (numbers or variables)
            stack[++stackTop] = token[0];
        } else if (token[0] == '(') {
            // left parenthesis - push to stack
            stack[++stackTop] = '(';
        } else if (token[0] == ')') {
            // right parenthesis - pop until left parenthesis
            while (stackTop >= 0 && stack[stackTop] != '(') {
                char arg2 = stack[stackTop--];
                char arg1 = stack[stackTop--];
                char operator = stack[stackTop--];
                char result = generateTempVar(tempCount++);
                
                tac[tacCount].op = operator;
                tac[tacCount].result = result;
                tac[tacCount].arg1 = arg1;
                tac[tacCount].arg2 = arg2;
                tacCount++;
                
                stack[++stackTop] = result;
            }
            stackTop--; // pop the '('
        } else if (token[0] == '+' || token[0] == '-' || token[0] == '*' || token[0] == '/') {
            // operator
            while (stackTop >= 1 && precedence(stack[stackTop - 1]) >= precedence(token[0])) {
                char arg2 = stack[stackTop--];
                char arg1 = stack[stackTop--];
                char operator = stack[stackTop--];
                char result = generateTempVar(tempCount++);
                
                tac[tacCount].op = operator;
                tac[tacCount].result = result;
                tac[tacCount].arg1 = arg1;
                tac[tacCount].arg2 = arg2;
                tacCount++;
                
                stack[++stackTop] = result;
            }
            stack[++stackTop] = token[0];
        }
    }

    // generate final result
    while (stackTop >= 1) {
        char arg2 = stack[stackTop--];
        char arg1 = stack[stackTop--];
        char operator = stack[stackTop--];
        char result = generateTempVar(tempCount++);
        
        tac[tacCount].op = operator;
        tac[tacCount].result = result;
        tac[tacCount].arg1 = arg1;
        tac[tacCount].arg2 = arg2;
        tacCount++;
    }

    // print TAC instructions
    printf("Three-Address Code:\n");
    for (int i = 0; i < tacCount; i++) {
        printf("%c = %c %c %c\n", tac[i].result, tac[i].arg1, tac[i].op, tac[i].arg2);
    }
}

int main() {
    // input expression
    char expr[] = "a + (b * c) / 5 - 8";
    printf("Input:\n");
	printf("a + (b * c) / 5 - 8\n");

    char tokens[MAX_LEN][MAX_LEN];
    int tokenCount = 0;

    tokenize(expr, tokens, &tokenCount);

    parseToTAC(tokens, tokenCount);

    return 0;
}