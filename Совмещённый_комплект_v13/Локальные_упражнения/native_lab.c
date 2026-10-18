#include <stdint.h>
#include <stdio.h>
#include <string.h>

int add(int a, int b) { return a + b; }

int accepts(const char *text) {
    static const unsigned char expected[] = {0x61, 0x62, 0x63};
    if (strlen(text) != sizeof expected) return 0;
    for (size_t i = 0; i < sizeof expected; ++i)
        if (((unsigned char)text[i] ^ 0x20u) != expected[i]) return 0;
    return 1;
}

int main(int argc, char **argv) {
    uint32_t value = UINT32_C(0x12345678);
    const unsigned char *bytes = (const unsigned char *)&value;
    printf("sum=%d\n", add(2, 3));
    printf("bytes=%02x %02x %02x %02x\n", bytes[0], bytes[1], bytes[2], bytes[3]);
    if (argc > 1) printf("accepted=%d\n", accepts(argv[1]));
    int count = 0;
    printf("ABCD%n", &count);
    printf(" count=%d\n", count);
    return 0;
}
