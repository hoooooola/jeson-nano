#!/bin/bash
set -e

# Config
CONTAINER_NAME="amr_sim"
WORKSPACE_DIR="/home/dev/workspace/shared"

echo "============================================="
echo "   Unified Simulation Launcher (One-Click)   "
echo "============================================="

# 1. Select Vehicle
echo "Select Vehicle Type:"
echo "1) ArduCopter (Multirotor)"
echo "2) ArduRover  (Ground Vehicle)"
echo "3) ArduPlane  (Fixed Wing)"
read -p "Enter choice [1-3]: " v_choice

case $v_choice in
    1) VEHICLE="ArduCopter";;
    2) VEHICLE="ArduRover";;
    3) VEHICLE="ArduPlane";;
    *) echo "Invalid choice"; exit 1;;
esac

# 2. Select Frame (Only for Copter)
PARAM_FILE=""
if [ "$VEHICLE" == "ArduCopter" ]; then
    echo ""
    echo "Select Frame Type:"
    echo "1) Quad X (Default)"
    echo "2) Hexa X"
    echo "3) Octo X"
    read -p "Enter choice [1-3]: " f_choice

    case $f_choice in
        1) PARAM_FILE="$WORKSPACE_DIR/params/copter_quad_x.parm";;
        2) PARAM_FILE="$WORKSPACE_DIR/params/copter_hexa_x.parm";;
        3) PARAM_FILE="$WORKSPACE_DIR/params/copter_octo_x.parm";;
        *) echo "Invalid choice"; exit 1;;
    esac
fi

echo ""
echo "Launching: $VEHICLE w/ Params: $PARAM_FILE"
echo "============================================="

# 3. Ensure Container is Running
./run_sim.sh > /dev/null 2>&1
echo "[Host] Container Running."

# 4. Construct Commands
CMD_GAZEBO="sudo docker exec -it $CONTAINER_NAME gz sim -v4 -r iris_runway.sdf"
CMD_SITL="sudo docker exec -it $CONTAINER_NAME $WORKSPACE_DIR/start_sitl.sh $VEHICLE $PARAM_FILE"
CMD_MAVROS="sudo docker exec -it $CONTAINER_NAME $WORKSPACE_DIR/start_mavros.sh"
CMD_QGC="./QGroundControl-x86_64.AppImage"

# 5. Launch in Gnome Terminal Tabs
# Check if qgc exists
if [ ! -f "QGroundControl-x86_64.AppImage" ]; then
    echo "Warning: QGC not found. Skipping QGC tab."
    CMD_QGC="echo 'QGC not found'; bash"
fi

gnome-terminal \
    --tab --title="Gazebo (Physics)" -- bash -c "$CMD_GAZEBO; exec bash" \
    --tab --title="ArduPilot (SITL)" -- bash -c "sleep 2; $CMD_SITL; exec bash" \
    --tab --title="MAVROS (Bridge)" -- bash -c "sleep 5; $CMD_MAVROS; exec bash" \
    --tab --title="QGroundControl" -- bash -c "sleep 3; $CMD_QGC; exec bash"

echo "All systems launched!"
