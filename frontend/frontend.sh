#!/bin/bash

COMPOSE_FILE="docker-compose.yaml"

build_frontend() {
    echo "Building frontend Docker service..."
    docker-compose -f $COMPOSE_FILE build frontend
}

run_frontend() {
    echo "Running frontend Docker service..."
    docker-compose -f $COMPOSE_FILE --compatibility up -d frontend
}

case "$1" in
    "build")
        build_frontend
        ;;
    "run")
        run_frontend
        ;;
    *)
        echo "Usage: $0 {build|run}"
        exit 1
        ;;
esac

exit 0
