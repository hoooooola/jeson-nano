#!/bin/bash
set -e

# Default Home Location (Taipei 101 area)
LOCATION="25.033964,121.564468,10,270"

# Derived paths based on container structure
# Assuming we are in /home/dev/workspace/shared/ardupilot
BINARY_PATH="/home/dev/workspace/shared/ardupilot/build/sitl/bin/arducopter"
DEFAULTS_PATH="/home/dev/workspace/shared/ardupilot/Tools/autotest/default_params/copter.parm"

# Defaults
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
# --model "JSON": Use JSON interface
# --serial0 tcp:0: Console on TCP 5760
# --serial1 udp:0.0.0.0:14550: MAVLink out to Host/QGC
# --sim-port-in 9002: Listen for Gazebo connection (JSON)
# Removed --sim-address to rely on default binding behavior
exec "$BINARY_PATH" \
    -S \
    -I 0 \
    --home "$LOCATION" \
    --model "JSON" \
    --speedup 1 \
    --defaults "$DEFAULTS_PATH" \
    --serial0 tcp:0 \
    --serial1 udp:0.0.0.0:14550 \
    --sim-port-in 9002
