#!/bin/bash
echo "=== Manual Download Required ==="
echo "Due to network/URL issues, please download QGroundControl manually:"
echo ""
echo "1. Go to: https://github.com/mavlink/qgroundcontrol/releases/latest"
echo "2. Download the 'QGroundControl.AppImage' file."
echo "3. Move it to this directory: $(pwd)"
echo "4. Run: chmod +x QGroundControl.AppImage"
echo ""
echo "After that, you can run start_qgc.sh or ./QGroundControl.AppImage"
exit 0
