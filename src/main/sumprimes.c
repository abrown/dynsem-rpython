#include <stdio.h>
#include <stdlib.h>

int main (int argc, char **argv) {
    int max = atoi(argv[1]);
    int s = 0;
    int n = 2;

    while (n <= max) {
        int p = 1;
        int d = 2;
        while (d <= (n - 1)){
            int m = d * (n / d);
            if (n <= m) {
                p = 0;
            }
            d += 1;
        }
        if (p) {
            s += n;
        }
        n += 1;
    }

    printf("%d\n", s);
    return 0;
}

