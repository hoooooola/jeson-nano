#!/bin/bash
set -e

source /opt/ros/humble/setup.bash

# Execute the command passed into this entrypoint
exec "$@"
