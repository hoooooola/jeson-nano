#!/bin/bash
set -e

# Allow X11 connections from Docker
echo "Allowing X11 connections..."
xhost +local:docker

# Start the container in detached mode
echo "Starting Simulation Container..."
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Remove old container if exists
docker rm -f amr_sim 2>/dev/null || true

# Direct Docker Run (Bypassing docker-compose due to version issues)
docker run -itd \
    --name amr_sim \
    --network host \
    --privileged \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "$SCRIPT_DIR":/home/dev/workspace/shared:rw \
    --device /dev/dri:/dev/dri \
    jeson_ecosys/simulation:latest \
    bash

# Enter the container unless -d flag is provided
if [ "$1" != "-d" ]; then
    echo "Entering Simulation Environment..."
    docker exec -it amr_sim bash
else
    echo "Container started in background."
fi
