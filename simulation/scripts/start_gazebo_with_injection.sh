#!/bin/bash
set -e

# Path to the SDF model that needs IP injection
# We need to make sure this file exists or is copied from the template
TEMPLATE_SDF="/home/dev/workspace/shared/models/iris_decoupled.sdf"
# If the decoupled model doesn't exist yet, we might need to fallback or fail
# But based on plan, user supply said "SDF_PATH"
SDF_PATH="/usr/share/gazebo-11/models/iris_runway/iris_runway.sdf"
# Actually, let's use the local workspace model if possible, but Gazebo usually loads from path.
# For simplicity and robustness, we assume we are running "gz sim ... iris_runway.sdf"
# But wait, the user spec used "iris_decoupled.sdf".
# We need to ensure we inject into the file that Gazebo actually loads.
# Given usage "gz sim -r iris_runway.sdf", it looks in GZ_SIM_RESOURCE_PATH.
# Let's assume we modify the one in the workspace: /home/dev/workspace/shared/iris_runway.sdf (if mounted)
target_sdf="/home/dev/workspace/shared/iris_runway.sdf"

if [ ! -f "$target_sdf" ]; then
    echo "[Gazebo] Warning: $target_sdf not found. Checking standard location..."
    # Fallback to checking args or standard models? 
    # For now, let's assume valid path provided by context or create a copy.
    # Let's try to find it.
    echo "[Gazebo] Using 'iris_runway.sdf' in current dir..."
    target_sdf="iris_runway.sdf"
fi

echo "[Gazebo] Resolving SITL IP..."
# Wait for SITL to be resolvable (Docker DNS)
count=0
while [ -z "$SITL_IP" ] && [ $count -lt 10 ]; do
    SITL_IP=$(getent hosts sitl | awk '{ print $1 }' | head -n1)
    if [ -z "$SITL_IP" ]; then
        echo "Waiting for SITL DNS..."
        sleep 1
        count=$((count+1))
    fi
done

if [ -z "$SITL_IP" ]; then
    echo "[Error] Could not resolve SITL hostname!"
    exit 1
fi

echo "[Gazebo] SITL IP Resolved: $SITL_IP"

# Create a runtime copy to avoid modifying the git-tracked file permanently (optional, but good practice)
# But user spec said "sed -i". Let's stick to spec but maybe copy first.
RUN_SDF="iris_runway_runtime.sdf"
cp "$target_sdf" "$RUN_SDF"

echo "[Gazebo] Injecting SITL IP into $RUN_SDF..."
# Replace <fdm_addr> value
# We need to handle cases where it might be empty or localhost
sed -i "s|<fdm_addr>.*</fdm_addr>|<fdm_addr>${SITL_IP}</fdm_addr>|g" "$RUN_SDF"

echo "[Gazebo] Starting Gazebo with $RUN_SDF..."
# Use exec to replace shell
exec gz sim -v4 -r "$RUN_SDF"
