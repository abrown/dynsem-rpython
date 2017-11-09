#include <stdio.h>
#include <stdlib.h>

// see http://lampwww.epfl.ch/teaching/archive/advanced_compiler/2007/resources/slides/act-2007-03-interpreters-vms_6.pdf
void interpret(int limit) {
 int term = 0;
 goto is_done; /* jump to first instruction */

 inc:
    term++;
    goto is_done; /* jump to next instruction */

 is_done:
    if (term >= limit)
        goto end; /* jump to next instruction */
    else
        goto inc; /* jump to next instruction */

 end:
    printf("Finished: %d\n", term);
}

int main(int argc, char* argv[]){
    if(argc != 2){
        printf("Expected one numeric argument passed, e.g. program 1000\n");
        return 1;
    }

    int limit = atoi(argv[1]);
    interpret(limit);
    return 0;
}