#!/bin/bash
set -e

# Default Home Location (Taipei 101 area)
LOCATION="25.033964,121.564468,10,270"

# Derived paths based on container structure
# Assuming we are in /home/dev/workspace/shared/ardupilot
BINARY_PATH="/home/dev/workspace/shared/ardupilot/build/sitl/bin/arducopter"
DEFAULTS_PATH="/home/dev/workspace/shared/ardupilot/Tools/autotest/default_params/copter.parm"

echo "[SITL] Starting ArduCopter Binary directly..."
echo "[SITL] Binary: $BINARY_PATH"
echo "[SITL] Location: $LOCATION"

# Ensure binary exists
if [ ! -f "$BINARY_PATH" ]; then
    echo "Error: Binary not found at $BINARY_PATH"
    echo "Please ensure SITL is built (run: ./waf configure --board sitl && ./waf copter)"
    exit 1
fi

# Launch ArduCopter
# -S: Synthetic Clock (speedup)
# -I 0: Instance 0
# --model "gazebo-iris": Use JSON interface
# -A udp:0.0.0.0:14550: MAVLink out to Host/QGC
# --model-input-port 9002: Listen for Gazebo connection (JSON)
exec "$BINARY_PATH" \
    -S \
    -I 0 \
    --home "$LOCATION" \
    --model "gazebo-iris" \
    --speedup 1 \
    --defaults "$DEFAULTS_PATH" \
    -A udp:0.0.0.0:14550 \
    --model-input-port 9002
