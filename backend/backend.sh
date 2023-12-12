#!/bin/bash

COMPOSE_FILE="compose.yaml"

if [[ "$1" == "gpu" ]]; then
    COMPOSE_FILE="compose-gpu.yaml"
    shift
fi

build_services() {
    if [ $# -eq 0 ]; then
        echo "Building all docker services"
        docker-compose -f $COMPOSE_FILE build
        return
    fi

    for service in "$@"; do
        echo "Building Docker service: $service"
        docker-compose -f $COMPOSE_FILE build "$service"
    done
}

run_services() {
    echo "Running Docker services..."
    docker-compose -f $COMPOSE_FILE --compatibility up -d
}

case "$1" in
    "build")
        shift
        build_services "$@"
        ;;
    "run")
        run_services
        ;;
    *)
        echo "Usage: $0 {gpu} build|run"
        exit 1
        ;;
esac

exit 0