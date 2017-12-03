#include <stdio.h>

int main () {
    int max = 1000;
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

