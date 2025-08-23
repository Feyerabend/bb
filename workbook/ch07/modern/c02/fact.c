#include <stdio.h>

void factorial();

int n;
int fact;
int i;

void factorial() {
	fact = 1;
	i = 1;
	while ((i <= n)) {
		fact = (fact * i);
		i = (i + 1);
	}
}


int main() {
	scanf("%d", &n);
	factorial();
	printf("%d\n", fact);
		return 0;
}