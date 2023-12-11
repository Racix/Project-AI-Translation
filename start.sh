#!/bin/bash
cd ./backend
./backend.sh build
./backend.sh run
cd ../frontend
./frontend.sh build
./frontend.sh run