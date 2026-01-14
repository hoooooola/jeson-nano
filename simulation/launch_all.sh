#!/bin/bash
set -u

SESSION="ardu_sim"
WORKSPACE_DIR="/home/dev/workspace/shared"
# Container names must match docker-compose.yml
CONTAINER_GAZEBO="amr_sim"
CONTAINER_SITL="sitl_runner"

# ==============================================================================
# Helper Functions
# ==============================================================================

check_docker_group() {
    if ! docker ps > /dev/null 2>&1; then
        echo "Error: Cannot connect to Docker daemon."
        echo "Please ensure you have permission to run docker commands."
        exit 1
    fi
}

cleanup_old_processes() {
    echo "Checking for existing sessions..."
    if tmux has-session -t $SESSION 2>/dev/null; then
        echo "Killing previous session '$SESSION'..."
        tmux kill-session -t $SESSION
    fi
}

select_frame() {
    echo "============================================="
    echo "   ArduPilot Decoupled Simulation Launcher   "
    echo "============================================="
    echo "Select Vehicle & Frame:"
    echo "1) Copter - Quad X (Default)"
    echo "2) Copter - Hexa X"
    echo "3) Copter - Octo X"
    echo "4) Plane"
    echo "5) Rover"
    echo "---------------------------------------------"
    read -p "Enter choice [1-5]: " choice
    
    case $choice in
        1) 
            VEHICLE="ArduCopter"
            PARAM_FILE="$WORKSPACE_DIR/params/copter_quad_x.parm"
            FRAME_MSG="Quad X"
            ;;
        2) 
            VEHICLE="ArduCopter"
            PARAM_FILE="$WORKSPACE_DIR/params/copter_hexa_x.parm"
            FRAME_MSG="Hexa X"
            ;;
        3) 
            VEHICLE="ArduCopter"
            PARAM_FILE="$WORKSPACE_DIR/params/copter_octo_x.parm"
            FRAME_MSG="Octo X"
            ;;
        4) 
            VEHICLE="ArduPlane"
            PARAM_FILE=""
            FRAME_MSG="Fixed Wing"
            ;;
        5) 
            VEHICLE="ArduRover"
            PARAM_FILE=""
            FRAME_MSG="Ground Rover"
            ;;
        *) 
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
    
    echo "Selected: $VEHICLE ($FRAME_MSG)"
    sleep 1
}

ensure_services() {
    echo "🚀 Starting Simulation Services (Bridge Network: sim_net)..."
    
    # Start the full stack (Gazebo + SITL) using Docker Compose V2 with 'sim' profile
    docker compose --profile sim up -d
    
    echo "Waiting for services to initialize..."
    sleep 3
    
    # Verify containers are running
    if ! docker ps | grep -q "$CONTAINER_SITL"; then
        echo "❌ Error: SITL container ($CONTAINER_SITL) failed to start."
        exit 1
    fi
    
    if ! docker ps | grep -q "$CONTAINER_GAZEBO"; then
        echo "❌ Error: Gazebo container ($CONTAINER_GAZEBO) failed to start."
        exit 1
    fi
    
    echo "✅ Services are running."
}

# ==============================================================================
# Main Execution
# ==============================================================================

# 1. Pre-flight Checks
check_docker_group
cleanup_old_processes
select_frame
ensure_services

# 2. Create Session & Layout
# Window 0: Gazebo (Main) - Monitor Logs
echo "Starting tmux session..."
tmux new-session -d -s $SESSION -n 'Gazebo'
tmux send-keys -t $SESSION:Gazebo "docker compose logs -f $CONTAINER_GAZEBO" C-m

# Window 1: SITL (Decoupled Container) - Monitor Logs
# SITL is now started automatically. We just watch the output.
tmux new-window -t $SESSION -n 'SITL'
tmux send-keys -t $SESSION:SITL "docker compose logs -f $CONTAINER_SITL" C-m

# Window 2: MAVROS
# MAVROS is currently embedded in the Gazebo container (amr_sim).
# We exec into it to start/monitor MAVROS if it's not part of the entrypoint.
tmux new-window -t $SESSION -n 'MAVROS'
tmux send-keys -t $SESSION:MAVROS "echo 'Monitoring MAVROS...'" C-m
# Assuming MAVROS is auto-started or needs manual start?
# For now, let's keep it manual or log watch if it's part of gazebo container startup.
# If start_gazebo_with_injection.sh starts MAVROS backgrounded, we check logs.
# If not, users might want a shell.
tmux send-keys -t $SESSION:MAVROS "docker exec -it $CONTAINER_GAZEBO bash" C-m

# Window 3: QGC
tmux new-window -t $SESSION -n 'QGC'
if [ -f "./QGroundControl-x86_64.AppImage" ]; then
    tmux send-keys -t $SESSION:QGC "./QGroundControl-x86_64.AppImage" C-m
else
    tmux send-keys -t $SESSION:QGC "echo 'QGC AppImage not found. Skipped.'" C-m
fi

# 3. Attach
tmux select-window -t $SESSION:Gazebo
echo "Attaching to session..."
tmux attach -t $SESSION

