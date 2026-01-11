#!/bin/bash
set -e

# Source ROS 2 environment
source /opt/ros/humble/setup.bash

echo "=== Starting MAVROS (UDP Bridge) ==="
echo "FCU URL: udp://:14551@"
echo "GCS URL: udp://@localhost:14550"

# Launch MAVROS
# fcu_url: The UDP port where MAVROS listens for MAVLink heartbeat from SITL
# gcs_url: Forward MAVLink traffic to QGC (usually listening on 14550)
ros2 launch mavros apm.launch fcu_url:=udp://:14551@ gcs_url:=udp://@localhost:14550 tgt_system:=1 tgt_component:=1 log_output:=screen
