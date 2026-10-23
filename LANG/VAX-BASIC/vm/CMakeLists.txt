cmake_minimum_required(VERSION 3.10)
project(vms_vm C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

include_directories(include)

set(SOURCES
    src/main.c
    src/vm.c
    src/rms.c
    src/runtime.c
)

add_executable(vms_vm ${SOURCES})

find_package(SQLite3 REQUIRED)
include_directories(${SQLite3_INCLUDE_DIRS})
target_link_libraries(vms_vm ${SQLite3_LIBRARIES} m)
