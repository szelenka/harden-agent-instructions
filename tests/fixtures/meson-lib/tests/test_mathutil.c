#include <assert.h>
#include "mathutil.h"

int main(void) {
    assert(factorial(0) == 1);
    assert(factorial(5) == 120);
    assert(fibonacci(0) == 0);
    assert(fibonacci(6) == 8);
    return 0;
}
