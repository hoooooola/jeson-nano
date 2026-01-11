#!/bin/bash
set -u

SESSION="ardu_sim"
WORKSPACE_DIR="/home/dev/workspace/shared"
CONTAINER_NAME="amr_sim"

# ==============================================================================
# Helper Functions
# ==============================================================================

check_docker_group() {
    # Check distinct actual access instead of just group membership string
    # This supports both 'usermod' (active session) and 'chmod 666' (dirty fix)
    if ! docker ps > /dev/null 2>&1; then
        echo "Error: Cannot connect to Docker daemon."
        echo "Please ensure you have permission to run docker commands."
        echo "  Standard Fix: sudo usermod -aG docker \$USER (then logout/login)"
        echo "  Quick/Dirty Fix: sudo chmod 666 /var/run/docker.sock"
        exit 1
    fi
}

select_frame() {
    echo "============================================="
    echo "   ArduPilot Simulation Launcher (tmux)      "
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

ensure_container() {
    echo "Checking Container Status..."
    if ! docker ps --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
        echo "Container not running. Starting with Profile 'sim'..."
        # Use --profile sim to match the new docker-compose.yml
        # Bypassing the old run_sim.sh to use clean docker compose w/ profiles
        docker compose --profile sim up -d
        
        echo "Waiting for container to initialize..."
        sleep 3
    else
        echo "Container $CONTAINER_NAME is already running."
    fi
}

# ==============================================================================
# Main Execution
# ==============================================================================

# 1. Pre-flight Checks
check_docker_group
select_frame
ensure_container

# 2. Check/Kill existing session to avoid conflict
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "Killing previous session '$SESSION'..."
    tmux kill-session -t $SESSION
fi

# 3. Create Session & Layout
# Window 0: Gazebo (Main)
# Uses 'docker exec' directly. No sudo needed (implied by step 1 check).
echo "Starting tmux session..."
tmux new-session -d -s $SESSION -n 'Gazebo'
tmux send-keys -t $SESSION:Gazebo "docker exec -it $CONTAINER_NAME gz sim -v4 -r iris_runway.sdf" C-m

# Window 1: SITL
# Wait for Gazebo to be ready (dumb sleep for now, better would be port check)
# But SITL connects TO Gazebo, so Gazebo should be up first.
tmux new-window -t $SESSION -n 'SITL'
tmux send-keys -t $SESSION:SITL "echo 'Waiting for Gazebo...'; sleep 3" C-m
tmux send-keys -t $SESSION:SITL "docker exec -it $CONTAINER_NAME $WORKSPACE_DIR/start_sitl.sh $VEHICLE $PARAM_FILE" C-m

# Window 2: MAVROS
tmux new-window -t $SESSION -n 'MAVROS'
tmux send-keys -t $SESSION:MAVROS "echo 'Waiting for SITL...'; sleep 8" C-m
tmux send-keys -t $SESSION:MAVROS "docker exec -it $CONTAINER_NAME $WORKSPACE_DIR/start_mavros.sh" C-m

# Window 3: QGC
# Running on HOST
tmux new-window -t $SESSION -n 'QGC'
if [ -f "./QGroundControl-x86_64.AppImage" ]; then
    tmux send-keys -t $SESSION:QGC "./QGroundControl-x86_64.AppImage" C-m
else
    tmux send-keys -t $SESSION:QGC "echo 'QGC AppImage not found. Skipped.'" C-m
fi

# 4. Attach
# Switch focus to Gazebo window
tmux select-window -t $SESSION:Gazebo
echo "Attaching to session..."
tmux attach -t $SESSION
