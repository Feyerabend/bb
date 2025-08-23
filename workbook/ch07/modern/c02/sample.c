#include <stdio.h>


int x;

int main() {
	x = 5;
	while ((x > 0)) {
		printf("%d\n", x);
		x = (x - 1);
	}
		return 0;
}