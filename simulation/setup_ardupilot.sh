#!/bin/bash
set -e

TARGET_DIR="/home/dev/workspace/shared/ardupilot"

echo "=== Setting up ArduPilot Source Code ==="

if [ ! -d "$TARGET_DIR" ]; then
    echo "Cloning ArduPilot to $TARGET_DIR..."
    git clone https://github.com/ArduPilot/ardupilot.git $TARGET_DIR
    cd $TARGET_DIR
    echo "Updating submodules (this may take a while)..."
    git submodule update --init --recursive
else
    echo "ArduPilot directory already exists at $TARGET_DIR."
fi

echo "=== Configuring Environment ==="
# Add ArduPilot tools to PATH in .bashrc if not already there
if ! grep -q "ardupilot/Tools/autotest" ~/.bashrc; then
    echo "Adding ArduPilot tools to PATH..."
    echo "export PATH=\$PATH:$TARGET_DIR/Tools/autotest" >> ~/.bashrc
    echo "export PATH=\$PATH:$TARGET_DIR/Tools/autotest" >> ~/.profile
else
    echo "PATH already configured."
fi

echo "=== Setup Complete ==="
echo "Please run: source ~/.bashrc"
