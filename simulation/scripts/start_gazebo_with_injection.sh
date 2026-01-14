#!/bin/bash
set -e

# Source SDF (System Path in container)
SDF_PATH="/home/dev/workspace/src/ardupilot_gazebo/worlds/iris_runway.sdf"
# Runtime copy (in shared volume)
RUN_SDF="/home/dev/workspace/shared/iris_runway_runtime.sdf"

echo "[Gazebo] Checking for Iris Model..."
if [ ! -f "$SDF_PATH" ]; then
    echo "[Error] SDF model not found at $SDF_PATH"
    echo "Listing /home/dev/workspace/src:"
    find /home/dev/workspace/src -name "*.sdf" | head -n 5
    exit 1
fi

echo "[Gazebo] Resolving SITL IP..."
count=0
while [ -z "$SITL_IP" ] && [ $count -lt 30 ]; do
    SITL_IP=$(getent hosts sitl | awk '{ print $1 }' | head -n1)
    if [ -z "$SITL_IP" ]; then
        echo "Waiting for SITL DNS... ($count/30)"
        sleep 1
        count=$((count+1))
    fi
done

if [ -z "$SITL_IP" ]; then
    echo "[Error] Could not resolve SITL hostname!"
    exit 1
fi

echo "[Gazebo] SITL IP Resolved: $SITL_IP"

echo "[Gazebo] Creating runtime SDF: $RUN_SDF"
cp "$SDF_PATH" "$RUN_SDF"

echo "[Gazebo] Injecting SITL IP into runtime SDF..."
# Replace any existing <fdm_addr> content with resolved IP
sed -i "s|<fdm_addr>.*</fdm_addr>|<fdm_addr>${SITL_IP}</fdm_addr>|g" "$RUN_SDF"

echo "[Gazebo] Starting Gazebo Harmonic..."
# Run gz sim (Server + GUI)
# -v4: Verbose logging
# -r: Run immediately (no pause)
exec gz sim -v4 -r "$RUN_SDF"
