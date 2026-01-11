#!/bin/bash
set -e

# Allow X11 connections from Docker
echo "Allowing X11 connections..."
xhost +local:docker

# Start the container in detached mode
echo "Starting Simulation Container..."
sudo docker-compose up -d

# Enter the container
echo "Entering Simulation Environment..."
sudo docker exec -it amr_sim bash
