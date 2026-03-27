.PHONY: configure build test lint clean

configure:
	cmake -B build -DCMAKE_BUILD_TYPE=Release

build: configure
	cmake --build build

test: build
	ctest --test-dir build --output-on-failure

lint:
	clang-tidy src/*.cpp -- -Iinclude -std=c++20

clean:
	rm -rf build
