#pragma once

#include <string>

namespace service {

struct Request {
    std::string method;
    std::string path;
    std::string body;
};

struct Response {
    int status;
    std::string body;
};

Response handle(const Request& req);

}  // namespace service
