cmake_minimum_required(VERSION 3.10.0)
project(PSI VERSION 0.0.1)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CXX_CLANG_TIDY clang-tidy)

add_compile_options(-Wall -Wextra -Werror -pedantic)

add_subdirectory(src)
