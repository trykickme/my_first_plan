/* format [one-byte length][data]. No network, no persistent state. */
#include <stddef.h>
#include <stdint.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 1) return 0;
    size_t wanted = data[0];
#ifndef SHOW_BUG
    if (wanted > size - 1) return 0;
#endif
    volatile uint8_t checksum = 0;
    for (size_t i = 0; i < wanted; i++) {
        checksum ^= data[i + 1];
    }
    (void)checksum;
    return 0;
}
