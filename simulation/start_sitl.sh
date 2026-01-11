#!/bin/bash
# 啟動 ArduPilot SITL for Gazebo Harmonic
# 此腳本會自動加上必要的參數 (-f JSON) 以避免通訊錯誤

echo "Starting ArduCopter SITL (QuadX) for Gazebo..."

# Check if we are inside the container
if [ ! -f "/.dockerenv" ]; then
    echo "Error: This script is intended to run INSIDE the Docker container."
    echo "Please run: sudo docker exec -it amr_sim bash"
    echo "Then run: ./start_sitl.sh"
    exit 1
fi

# Load Environment
source ~/.bashrc

# Launch SITL with correct flags
# -v ArduCopter: Select Vehicle
# -f JSON: Force JSON protocol for new Gazebo plugin compliance
# --console --map: Launch MAVProxy GUI
sim_vehicle.py -v ArduCopter -f JSON --console --map
