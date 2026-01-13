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
    
    # Start the full stack (Gazebo + SITL)
    # Using 'docker-compose' (V1) or 'docker compose' (V2) compatibility check
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
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
# Window 0: Gazebo (Main)
echo "Starting tmux session..."
tmux new-session -d -s $SESSION -n 'Gazebo'
tmux send-keys -t $SESSION:Gazebo "docker exec -it $CONTAINER_GAZEBO gz sim -v4 -r iris_runway.sdf" C-m

# Window 1: SITL (Decoupled Container)
# Connect to 'sitl' container
tmux new-window -t $SESSION -n 'SITL'
tmux send-keys -t $SESSION:SITL "echo 'Waiting for Gazebo...'; sleep 3" C-m
# IMPORTANT: We pass -I0 to ensure MAVLink binds to all interfaces (including the bridge IP)
# Actually start_sitl.sh handles the call. We might need to adjust it to listen on 0.0.0.0?
# In decoupled mode, SITL is the server for Gazebo plugin? Or Gazebo plugin connects to SITL?
# Standard ArduPilot Plugin: Gazebo connects to SITL TCP port, or SITL sends UDP?
# Usually SITL binds to port 5760 (TCP). Gazebo Plugin connects to SITL_IP:5760.
tmux send-keys -t $SESSION:SITL "docker exec -it $CONTAINER_SITL /bin/bash -c 'export LANG=en_US.UTF-8 && $WORKSPACE_DIR/start_sitl.sh $VEHICLE $PARAM_FILE'" C-m

# Window 2: MAVROS
tmux new-window -t $SESSION -n 'MAVROS'
tmux send-keys -t $SESSION:MAVROS "echo 'Waiting for SITL...'; sleep 8" C-m
# MAVROS runs in Gazebo container (as per docker-compose definition/legacy) or separate?
# Ideally separate, but for now it's in 'amr_sim' (Gazebo service) based on build?
# If MAVROS is in 'amr_sim', it needs to talk to 'sitl' hostname.
tmux send-keys -t $SESSION:MAVROS "docker exec -it $CONTAINER_GAZEBO $WORKSPACE_DIR/start_mavros.sh" C-m

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

