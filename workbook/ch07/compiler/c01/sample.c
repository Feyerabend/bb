#include <stdio.h>

void multiply();

int x;
int y;
int z;

void multiply() {
	z = 0;
	while ((x > 0)) {
		z = (z + y);
		x = (x - 1);
	}
}


int main() {
	scanf("%d", &x);
	scanf("%d", &y);
	multiply();
	printf("%d\n", z);
		return 0;
}