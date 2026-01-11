# 快速故障排除 - 腳本等待 Heartbeat

## 🔍 當前狀態

您的腳本正在等待 Heartbeat:
```
正在等待飛控 Heartbeat...
```

## ✅ Port 確認

Port 14551 **已經在監聽**:
```
udp   0.0.0.0:14551   (多個實例)
```

## 🎯 可能的原因和解決方案

### 原因 1: SITL 尚未完全啟動

**檢查方法**:
切換到 SITL 視窗 (tmux `Ctrl+b 1`) 查看是否顯示:
```
APM: ArduCopter V4.x.x
Ready to FLY
```

**解決方案**: 等待 SITL 完全啟動 (通常需要 10-15 秒)

---

### 原因 2: SITL 未解鎖

**症狀**: SITL 啟動了,但未解鎖

**解決方案**:
在 SITL 視窗執行:
```bash
mode GUIDED
arm throttle
```

---

### 原因 3: Port 14551 連接問題

**ArduPilot SITL 默認端口**:
- 14550: QGC
- 14551: MAVROS (需要 MAVROS 啟動才會有 heartbeat)
- 14552-14554: 其他客戶端

**解決方案**: 改用 14550 (與 QGC 共用,但測試時可接受)

修改 `safe_compass_interference.py` 第 23 行:
```python
# 原本
CONNECTION_STRING = 'udp:127.0.0.1:14551'

# 改為
CONNECTION_STRING = 'udp:127.0.0.1:14550'
```

---

### 原因 4: MAVROS 未啟動

Port 14551 通常是 MAVROS 使用的。如果 MAVROS 未啟動,可能沒有 heartbeat。

**檢查 MAVROS 狀態**:
切換到 MAVROS 視窗 (tmux `Ctrl+b 2`)

**解決方案**:
1. 確認 MAVROS 正在運行
2. 或改用 14550 端口

---

## 🚀 快速解決方案

### 方案 A: 使用 14550 (最簡單)

1. 按 `Ctrl+C` 停止當前腳本
2. 編輯腳本:
```bash
nano safe_compass_interference.py
# 修改第 23 行為: CONNECTION_STRING = 'udp:127.0.0.1:14550'
```
3. 重新執行:
```bash
python3 safe_compass_interference.py
```

### 方案 B: 等待 MAVROS 啟動

1. 切換到 MAVROS 視窗: `Ctrl+b 2`
2. 確認看到 "FCU: connected"
3. 腳本應該會自動連接

### 方案 C: 使用原始腳本

如果只是測試,可以直接用優化過的原始腳本:
```bash
# 按 Ctrl+C 停止當前腳本
python3 simulate_compass_interference.py
```

---

## 📝 建議執行順序

1. **確認 SITL 已啟動**
   ```bash
   # 在 SITL 視窗 (Ctrl+b 1)
   mode GUIDED
   arm throttle
   takeoff 10
   ```

2. **等待穩定** (10 秒)

3. **執行腳本**
   ```bash
   # 使用 14550 端口版本
   python3 safe_compass_interference.py
   ```

---

## 🔧 臨時修改指令

如果不想編輯文件,可以直接在終端執行:

```bash
# 停止當前腳本 (Ctrl+C)

# 使用 sed 臨時修改端口
sed 's/14551/14550/g' safe_compass_interference.py > temp_script.py
python3 temp_script.py
```

---

**最快解決**: 按 `Ctrl+C` 停止腳本,改用 `python3 simulate_compass_interference.py`
