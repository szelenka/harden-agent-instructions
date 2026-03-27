#include "handler.h"

namespace service {

Response handle(const Request& req) {
    if (req.path == "/health") {
        return {200, R"({"status":"ok"})"};
    }
    return {404, R"({"error":"not found"})"};
}

}  // namespace service
