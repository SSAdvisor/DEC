cmake_minimum_required(VERSION 3.10)
project(librsts_vm C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/main.c
    src/vm.c
    src/rms.c
    src/runtime.c
)

# Executable or library?
# We will ultimately compile this into an executable that includes the bytecode appended to it.
# For now, let's just make it a standard executable that can read bytecode from a file.
add_executable(rsts_vm ${SOURCES})

# Find SQLite3
find_package(SQLite3 REQUIRED)
include_directories(${SQLite3_INCLUDE_DIRS})
target_link_libraries(rsts_vm ${SQLite3_LIBRARIES})

# Find Math library
target_link_libraries(rsts_vm m)
