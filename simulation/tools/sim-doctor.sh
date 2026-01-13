#!/usr/bin/env bash
# sim-doctor — simulation sanity check
# Usage: ./sim-doctor.sh (run inside container or on host)

set -e

echo "🩺 sim-doctor — simulation sanity check"
echo "====================================="
echo

# ---------- GPU ----------
echo "🔹 [GPU] Checking /dev/dri and EGL"
if [ ! -d /dev/dri ]; then
  echo "❌ /dev/dri not present"
else
  ls -l /dev/dri
fi

if command -v eglinfo >/dev/null 2>&1; then
  RENDERER=$(eglinfo 2>/dev/null | grep -m1 "OpenGL renderer" || true)
  echo "Renderer: ${RENDERER:-<unknown>}"
elif command -v glxinfo >/dev/null 2>&1; then
  glxinfo | grep -E "OpenGL renderer|OpenGL vendor" || true
else
  echo "⚠️ No eglinfo / glxinfo available"
fi
echo

# ---------- SITL port ----------
echo "🔹 [SITL] Checking TCP 5760"
if ss -ltn | grep -q ":5760"; then
  echo "✅ SITL port 5760 is listening"
else
  echo "❌ SITL port 5760 NOT listening"
fi
echo

# ---------- MAVLink heartbeat ----------
echo "🔹 [MAVLink] Checking heartbeat"
timeout 3 bash -c '
  if command -v mavproxy.py >/dev/null 2>&1; then
    mavproxy.py --master tcp:127.0.0.1:5760 --cmd="status" --nowait 2>/dev/null | grep -q "SYSID"
  else
    echo "⚠️ mavproxy not installed"
    exit 1
  fi
' && echo "✅ Heartbeat detected" || echo "❌ No heartbeat"
echo

echo "🧾 User / Groups"
id
echo

echo "====================================="
echo "🩺 sim-doctor finished"
echo
echo "Quick Reference:"
echo "  Renderer = Intel/Mesa/iris  → GPU OK"
echo "  Renderer = llvmpipe         → CPU fallback"
echo "  5760 NOT listening          → SITL not started"
echo "  No heartbeat                → Gazebo/SITL timing issue"
