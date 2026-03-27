#include "handler.h"
#include <cassert>

int main() {
    auto resp = service::handle({"GET", "/health", ""});
    assert(resp.status == 200);

    auto not_found = service::handle({"GET", "/missing", ""});
    assert(not_found.status == 404);

    return 0;
}
