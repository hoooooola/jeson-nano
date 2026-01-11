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

# Ensure ArduPilot tools are in PATH (Robustness for One-Click Run)
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
ARDUPILOT_TOOLS="$SCRIPT_DIR/ardupilot/Tools/autotest"

if [[ ":$PATH:" != *":$ARDUPILOT_TOOLS:"* ]]; then
    if [ -d "$ARDUPILOT_TOOLS" ]; then
        echo "Adding ArduPilot tools to PATH: $ARDUPILOT_TOOLS"
        export PATH=$PATH:$ARDUPILOT_TOOLS
    else
        echo "Error: ArduPilot source not found at $ARDUPILOT_TOOLS"
        echo "Please ensure you have cloned ArduPilot into the simulation directory."
        exit 1
    fi
fi

# Launch SITL with correct flags
# -v ArduCopter: Select Vehicle
# -f JSON: Force JSON protocol for new Gazebo plugin compliance
# --console --map: Launch MAVProxy GUI
sim_vehicle.py -v ArduCopter -f JSON --console --map
