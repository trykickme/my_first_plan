/* alias does not acquire an independent lifetime. */
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *owner = malloc(sizeof(*owner));
    if (owner == NULL) return 1;
    *owner = 42;
    int *alias = owner;
    printf("before free: %d\n", *alias);
    free(owner);
    owner = NULL;
#ifdef SHOW_UAF
    printf("invalid access through alias: %d\n", *alias);
#else
    alias = NULL;
    puts("ownership ended; no further dereference");
#endif
    return 0;
}
