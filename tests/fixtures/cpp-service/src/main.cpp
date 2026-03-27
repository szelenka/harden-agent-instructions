#include "handler.h"
#include <iostream>

int main() {
    service::Request req{"GET", "/health", ""};
    auto resp = service::handle(req);
    std::cout << "Status: " << resp.status << "\n";
    return 0;
}
