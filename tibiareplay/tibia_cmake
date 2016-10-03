#!/bin/bash
case $1 in
  'all')
    mkdir -p build_release && cd build_release && cmake -G "MinGW Makefiles" .. -DCMAKE_BUILD_TYPE=release -DCMAKE_MAKE_PROGRAM=mingw32-make.exe
    cd ..
    mkdir -p build_debug && cd build_debug && cmake -G "MinGW Makefiles" .. -DCMAKE_BUILD_TYPE=debug -DCMAKE_MAKE_PROGRAM=mingw32-make.exe
    ;;

  'release')
    mkdir -p build_release && cd build_release && cmake -G "MinGW Makefiles" .. -DCMAKE_BUILD_TYPE=release -DCMAKE_MAKE_PROGRAM=mingw32-make.exe
    ;;

  'debug')
    mkdir -p build_debug && cd build_debug && cmake -G "MinGW Makefiles" .. -DCMAKE_BUILD_TYPE=debug -DCMAKE_MAKE_PROGRAM=mingw32-make.exe
    ;;

  *)
    echo "Usage: $0 [ all | release | debug ]"
    ;;
esac
