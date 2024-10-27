#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *input;
int pos = 0;

char lookahead() {
    return input[pos];
}

void eat(char expected) {
    if (lookahead() == expected) {
        pos++;
    } else {
        printf("Error: Expected %c but found %c\n", expected, lookahead());
        exit(1);
    }
}

void E();
void E_prime();
void T();
void T_prime();

void E() {
    T();
    E_prime();
}

void E_prime() {
    if (lookahead() == '+') {
        eat('+');
        T();
        E_prime();
    }
}

void T() {
    if (lookahead() == 'i') {  // assuming 'i' represents an integer
        eat('i');
        T_prime();
    } else if (lookahead() == '(') {
        eat('(');
        E();
        eat(')');
    }
}

void T_prime() {
    if (lookahead() == '*') {
        eat('*');
        T();
        T_prime();
    }
}

int main() {
    input = "i+i*i";  // example input
    E();
    if (lookahead() == '\0') {
        printf("Input parsed successfully!\n");
    } else {
        printf("Error: Unexpected input at end\n");
    }
    return 0;
}
