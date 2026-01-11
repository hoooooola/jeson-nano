#!/bin/bash

# 停止所有 ArduPilot SITL 相關進程
# 用途: 清理環境,準備重新啟動

set -e

echo "=========================================="
echo "停止 ArduPilot SITL 模擬環境"
echo "=========================================="

# 1. 停止 tmux session
echo ""
echo "[1/4] 停止 tmux session..."
if tmux has-session -t ardu_sim 2>/dev/null; then
  tmux kill-session -t ardu_sim
  echo "✓ tmux session 'ardu_sim' 已停止"
else
  echo "✓ 沒有運行中的 tmux session"
fi

# 2. 停止所有 MAVProxy 進程
echo ""
echo "[2/4] 停止 MAVProxy 進程..."
MAVPROXY_COUNT=$(pgrep -f mavproxy.py | wc -l)
if [ "$MAVPROXY_COUNT" -gt 0 ]; then
  pkill -9 -f mavproxy.py
  echo "✓ 已停止 $MAVPROXY_COUNT 個 MAVProxy 進程"
else
  echo "✓ 沒有運行中的 MAVProxy 進程"
fi

# 3. 停止所有 ArduCopter 進程
echo ""
echo "[3/4] 停止 ArduCopter 進程..."
ARDUCOPTER_COUNT=$(pgrep arducopter | wc -l)
if [ "$ARDUCOPTER_COUNT" -gt 0 ]; then
  pkill -9 arducopter
  echo "✓ 已停止 $ARDUCOPTER_COUNT 個 ArduCopter 進程"
else
  echo "✓ 沒有運行中的 ArduCopter 進程"
fi

# 4. 等待進程完全終止
echo ""
echo "[4/4] 等待進程完全終止..."
sleep 2

# 驗證清理完成
echo ""
echo "=========================================="
echo "驗證清理結果"
echo "=========================================="

REMAINING_MAVPROXY=$(pgrep -f mavproxy.py | wc -l)
REMAINING_ARDUCOPTER=$(pgrep arducopter | wc -l)

if [ "$REMAINING_MAVPROXY" -eq 0 ] && [ "$REMAINING_ARDUCOPTER" -eq 0 ]; then
  echo "✅ 所有進程已成功停止"
  echo ""
  echo "現在可以重新啟動: ./launch_all.sh"
else
  echo "⚠️  警告: 仍有進程未停止"
  echo "   MAVProxy: $REMAINING_MAVPROXY"
  echo "   ArduCopter: $REMAINING_ARDUCOPTER"
  echo ""
  echo "請手動檢查: ps aux | grep -E 'mavproxy|arducopter'"
fi

echo "=========================================="
