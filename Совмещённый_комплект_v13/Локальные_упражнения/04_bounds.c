/* own toy binary; SHOW_BUG deliberately removes the check. */
#include <stdio.h>
#include <stddef.h>

static int read_index(size_t index) {
    int values[4] = {10, 20, 30, 40};
#ifndef SHOW_BUG
    if (index >= sizeof(values) / sizeof(values[0])) {
        puts("rejected: index outside array");
        return 0;
    }
#endif
    printf("value[%zu] = %d\n", index, values[index]);
    return 0;
}

int main(void) {
    read_index(3);
    return read_index(4);
}
