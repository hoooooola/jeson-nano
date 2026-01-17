#!/bin/bash
set -e

echo "============================================"
echo "🔧 Setting up ArduPilot Gazebo Plugin"
echo "============================================"

# 1. Install prerequisites
echo " > Installing build tools and libignition-fortress-dev..."
sudo apt update
sudo apt install -y libfuse2 cmake build-essential libignition-fortress-dev

# 2. Clone the plugin repository
# We use the allowed workspace for this
TARGET_DIR="/media/user/windowsData1/gitClone/GitProject/jesonEcosys/ardupilot_gazebo"

if [ -d "$TARGET_DIR" ]; then
    echo " > Repo exists. Pulling latest..."
    cd "$TARGET_DIR" && git pull || true
else
    echo " > Cloning ardupilot_gazebo..."
    git clone https://github.com/ArduPilot/ardupilot_gazebo "$TARGET_DIR"
    cd "$TARGET_DIR"
    git checkout fortress
fi

# 3. Build the plugin
echo " > Building plugin..."
cd "$TARGET_DIR"
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j4

# 4. Environment Setup
echo " > Configuring environment..."
# Add to .bashrc if not present
GZ_MARKER="# ArduPilot Gazebo Plugin Configuration"
if ! grep -q "$GZ_MARKER" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "$GZ_MARKER" >> ~/.bashrc
    echo "export GZ_SIM_SYSTEM_PLUGIN_PATH=$TARGET_DIR/build:\$GZ_SIM_SYSTEM_PLUGIN_PATH" >> ~/.bashrc
    echo "export GZ_SIM_RESOURCE_PATH=$TARGET_DIR/models:$TARGET_DIR/worlds:\$GZ_SIM_RESOURCE_PATH" >> ~/.bashrc
    echo " > Added env vars to .bashrc"
    
    # Also export for current session interpretation by the user
    export GZ_SIM_SYSTEM_PLUGIN_PATH=$TARGET_DIR/build:$GZ_SIM_SYSTEM_PLUGIN_PATH
    export GZ_SIM_RESOURCE_PATH=$TARGET_DIR/models:$TARGET_DIR/worlds:$GZ_SIM_RESOURCE_PATH
else
    echo " > Env vars already present."
fi

echo "============================================"
echo "✅ Gazebo Plugin Setup Complete!"
echo "Please run: source ~/.bashrc"
echo "============================================"
