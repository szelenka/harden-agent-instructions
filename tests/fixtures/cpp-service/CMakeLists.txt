cmake_minimum_required(VERSION 3.20)
project(cpp-service VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(server src/main.cpp src/handler.cpp)
target_include_directories(server PRIVATE include)

enable_testing()
add_executable(tests tests/handler_test.cpp src/handler.cpp)
target_include_directories(tests PRIVATE include)
add_test(NAME unit_tests COMMAND tests)
