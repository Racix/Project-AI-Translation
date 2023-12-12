#!/bin/bash

cd ./backend
if [[ "$1" == "gpu" ]]; then
    ./backend.sh gpu build
    ./backend.sh gpu run
else
    ./backend.sh build
    ./backend.sh run
fi

cd ../frontend
./frontend.sh build
./frontend.sh run