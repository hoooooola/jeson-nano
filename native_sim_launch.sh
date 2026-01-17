#!/bin/bash

# Native ArduPilot + Gazebo Launch Script (Robust Tmux & QGC Support)
# Usage: ./native_sim_launch.sh

# QGC Location
QGC_PATH="/media/user/Linux_Extra/workspaces/qgc/QGroundControl.AppImage"

# ==========================================
# Phase 1: Parent Launcher (Outside Tmux)
# ==========================================
if [ -z "$TMUX" ]; then
    echo "============================================"
    echo "🚀 Starting ArduCopter SITL + Gazebo Fortress"
    echo "============================================"
    echo " > Vehicle: Copter"
    echo " > World:   gazebo-iris"
    echo " > Output:  Tmux + Map"
    echo " > GCS:     QGroundControl"
    echo "============================================"

    # 1. Kill any stale session
    tmux kill-session -t native_sim 2>/dev/null

    # 2. Start QGC in background
    if [ -f "$QGC_PATH" ]; then
        echo "Starting QGroundControl..."
        "$QGC_PATH" &> /dev/null &
        QGC_PID=$!
        echo " - QGC PID: $QGC_PID"
    else
        echo "Warning: QGroundControl not found at $QGC_PATH"
    fi

    # 3. Define cleanup trap (to kill QGC when we exit)
    cleanup() {
        echo "Shutting down..."
        [ -n "$QGC_PID" ] && kill "$QGC_PID" 2>/dev/null
        echo "Done."
    }
    trap cleanup EXIT

    # 4. Start Tmux Session (Blocking)
    # We call this script again, which will fall into Phase 2 because new-session spawns a shell
    SCRIPT_PATH=$(realpath "$0")
    echo "Starting Tmux Session..."
    tmux new-session -s native_sim "bash $SCRIPT_PATH; bash"

    # When tmux session ends (user detaches or closes), execution continues here -> trap fires -> QGC dies.
    exit 0
fi

# ==========================================
# Phase 2: Simulation Runner (Inside Tmux)
# ==========================================
echo "Loading environment..."
source ~/.bashrc
source /opt/ros/humble/setup.bash

# Check requirements
if ! command -v sim_vehicle.py &> /dev/null; then
    echo "Error: sim_vehicle.py not found!"
    echo "Ensure you have sourced your environment."
    exit 1
fi

echo "Launching ArduPilot SITL..."
# We don't use --tmux flag here, because we ARE already in tmux!
sim_vehicle.py -v Copter -f gazebo-iris --console --map
