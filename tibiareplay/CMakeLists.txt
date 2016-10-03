cmake_minimum_required(VERSION 3.0)

project(tibia-replay)

include(GenerateExportHeader)

add_definitions(-D_WIN32_WINNT=0x0502)

# Common compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Werror -pedantic -std=c++11 -fno-strict-aliasing")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -O0")

# tibia-replay.exe
set(tibia-replay_src
  "src/tibia-replay/tibia_replay.cc"
)

set(tibia-replay_inc
  "src/common"
)

set(tibia-replay_lib
  "Kernel32"
  "psapi"
)

add_executable(tibia-replay ${tibia-replay_src})
target_include_directories(tibia-replay PUBLIC ${tibia-replay_inc})
target_link_libraries(tibia-replay ${tibia-replay_lib})

# tibia-replay-dll.dll
set(tibia-replay-dll_src
  "src/tibia-replay-dll/tibia_replay_dll.cc"
  "src/tibia-replay-dll/tibia_connection.cc"
  "src/tibia-replay-dll/replay_reader.cc"
  "src/tibia-replay-dll/utils/console.cc"
  "src/tibia-replay-dll/utils/crc32.cc"
  "src/tibia-replay-dll/utils/keystroke.cc"
  "src/tibia-replay-dll/utils/rsa.cc"
  "src/tibia-replay-dll/utils/xtea.cc"
  "src/tibia-replay-dll/utils/obs.cc"
  "src/tibia-replay-dll/network/connection.cc"
  "src/tibia-replay-dll/network/ws2_32.cc"
)

set(tibia-replay-dll_inc
  "src/common"
)

set(tibia-replay-dll_lib
  "user32"
  "version"
  "winmm"
  "gmp"
)

add_library(tibia-replay-dll MODULE ${tibia-replay-dll_src})
target_include_directories(tibia-replay-dll PUBLIC ${tibia-replay-dll_inc})
target_link_libraries(tibia-replay-dll ${tibia-replay-dll_lib})
