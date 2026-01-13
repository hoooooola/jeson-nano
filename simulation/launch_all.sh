#!/bin/bash
set -u

SESSION="ardu_sim"
WORKSPACE_DIR="/home/dev/workspace/shared"
CONTAINER_NAME="amr_sim"

# SITL 專用持久化容器
SITL_CONTAINER_NAME="sitl_runner"
SITL_IMAGE="ardupilot/ardupilot-dev-base:latest"
SITL_WORKDIR="/home/dev/workspace/shared/ardupilot"

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

cleanup_old_processes() {
    echo "Checking for existing SITL processes..."
    
    # Count existing processes
    MAVPROXY_COUNT=$(pgrep -f mavproxy.py 2>/dev/null | wc -l)
    ARDUCOPTER_COUNT=$(pgrep arducopter 2>/dev/null | wc -l)
    
    if [ "$MAVPROXY_COUNT" -gt 0 ] || [ "$ARDUCOPTER_COUNT" -gt 0 ]; then
        echo "⚠️  Found existing processes:"
        echo "   MAVProxy instances: $MAVPROXY_COUNT"
        echo "   ArduCopter instances: $ARDUCOPTER_COUNT"
        echo ""
        echo "Cleaning up old processes..."
        
        # Kill old tmux session
        tmux kill-session -t $SESSION 2>/dev/null || true
        
        # Kill processes inside SITL container
        docker exec $SITL_CONTAINER_NAME pkill -9 -f mavproxy.py 2>/dev/null || true
        docker exec $SITL_CONTAINER_NAME pkill -9 arducopter 2>/dev/null || true
        
        # Kill processes on host (fallback)
        pkill -9 -f mavproxy.py 2>/dev/null || true
        pkill -9 arducopter 2>/dev/null || true
        
        # Wait for cleanup
        sleep 2
        echo "✓ Cleanup completed"
    else
        echo "✓ No existing processes found"
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
        echo "Container not running. Starting service 'sitl'..."
        # Use docker-compose (v1.29.2) instead of 'docker compose'
        # Start the 'sitl' service directly (which has profile 'sim')
        docker-compose up -d sitl
        
        echo "Waiting for container to initialize..."
        sleep 3
    else
        echo "Container $CONTAINER_NAME is already running."
    fi
}

# ==============================================================================
# SITL Persistent Container Functions (NEW)
# ==============================================================================

ensure_sitl_container() {
    echo "🔧 Checking SITL container ($SITL_CONTAINER_NAME)..."
    
    FIRST_RUN=false
    
    # 1. Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^${SITL_CONTAINER_NAME}$"; then
        echo "   → Container does not exist. Creating..."
        docker create \
            --name $SITL_CONTAINER_NAME \
            --net=host \
            --privileged \
            -u 0 \
            -v "$(pwd):/home/dev/workspace/shared" \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -e DISPLAY=$DISPLAY \
            -w $SITL_WORKDIR \
            $SITL_IMAGE \
            /bin/bash -c "while true; do sleep 3600; done"
        echo "   ✓ Container created"
        FIRST_RUN=true
    else
        echo "   ✓ Container exists"
    fi
    
    # 2. Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${SITL_CONTAINER_NAME}$"; then
        echo "   → Container not running. Starting..."
        docker start $SITL_CONTAINER_NAME
        sleep 2
        echo "   ✓ Container started"
    else
        echo "   ✓ Container already running"
    fi
    
    # 3. Ensure git safe.directory is set (idempotent)
    echo "   → Setting git safe.directory..."
    docker exec $SITL_CONTAINER_NAME git config --global --add safe.directory $SITL_WORKDIR 2>/dev/null || true
    echo "   ✓ Git configured"
    
    # 4. First-run setup: install MAVProxy and dependencies
    if [ "$FIRST_RUN" = true ] || ! docker exec $SITL_CONTAINER_NAME which mavproxy.py >/dev/null 2>&1; then
        echo "   → Running first-time setup (installing MAVProxy, etc.)..."
        docker exec -it $SITL_CONTAINER_NAME /bin/bash -c "cd $SITL_WORKDIR && ./setup_sitl_env.sh"
        echo "   ✓ First-time setup completed"
    else
        echo "   ✓ MAVProxy already installed"
    fi
}

ensure_sitl_ready() {
    echo "🔧 Checking SITL build status..."
    
    # Fixed path inside container
    SITL_BINARY="$SITL_WORKDIR/build/sitl/bin/arducopter"
    
    # Check if binary exists
    if docker exec $SITL_CONTAINER_NAME test -f "$SITL_BINARY"; then
        echo "   ✓ SITL binary exists. Skipping build."
        return 0
    fi
    
    echo "   → SITL binary not found. Running first-time setup..."
    
    # First-time setup: git safe.directory + setup_sitl_env.sh + build
    docker exec -it $SITL_CONTAINER_NAME /bin/bash -c "
        git config --global --add safe.directory $SITL_WORKDIR
        ./setup_sitl_env.sh
        export LANG=en_US.UTF-8
        export LC_ALL=en_US.UTF-8
        cd $SITL_WORKDIR/ArduCopter
        ../Tools/autotest/sim_vehicle.py -v ArduCopter --no-mavproxy -w
    "
    
    echo "   ✓ First-time setup completed"
}

# ==============================================================================
# Main Execution
# ==============================================================================

# 1. Pre-flight Checks
check_docker_group
cleanup_old_processes
select_frame
ensure_container
ensure_sitl_container

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

# Window 1: SITL (Persistent Container Mode)
# Only runs setup/build on first launch; subsequent launches are instant
tmux new-window -t $SESSION -n 'SITL'
tmux send-keys -t $SESSION:SITL "echo 'Waiting for Gazebo...'; sleep 3" C-m
tmux send-keys -t $SESSION:SITL "docker exec -it $SITL_CONTAINER_NAME /bin/bash -c 'export LANG=en_US.UTF-8 && export LC_ALL=en_US.UTF-8 && $WORKSPACE_DIR/start_sitl.sh $VEHICLE $PARAM_FILE'" C-m

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

