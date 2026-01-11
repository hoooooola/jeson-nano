# ArduPilot SITL 磁力計干擾模擬問題 - 完整上下文

## 🎯 目標
在 ArduPilot SITL 中透過 Python 腳本動態模擬磁力計干擾,讓 QGC 保持連線並能觀察到完整的干擾過程。

## 🔴 問題現象

### 問題 1: QGC 斷線
- **執行腳本**: `python3 simulate_compass_interference.py`
- **結果**: QGC 顯示 "Comms Lost" (通訊中斷)
- **腳本狀態**: 參數確實有改變,但過程太快

### 問題 2: Heartbeat 等待超時
- **執行腳本**: `python3 safe_compass_interference.py` (Port 14551)
- **結果**: 卡在 "正在等待飛控 Heartbeat..." 無法連接

### 問題 3: 改用 Port 14550 後 SITL 斷線
- **修改**: 將 Port 從 14551 改為 14550
- **結果**: SITL 斷線,沒有按照腳本工作

## 🔧 環境配置

### SITL 啟動方式
```bash
cd simulation
./launch_all.sh
# 選擇: 1 (ArduCopter) → 1 (Quad X)
```

### Docker 配置
```yaml
# docker-compose.yml
services:
  sitl:
    image: jeson_ecosys/simulation:latest
    container_name: amr_sim
    network_mode: host  # 使用 host 網路模式
```

### 端口狀態
```bash
$ netstat -tuln | grep 145
udp   0.0.0.0:14550   # QGC
udp   0.0.0.0:14551   # MAVROS (多個實例)
udp   0.0.0.0:14555
```

### SITL 狀態
- ✅ SITL 已啟動
- ✅ 已解鎖 (`arm throttle`)
- ✅ 已起飛 (`takeoff 10`)
- ✅ QGC 已連接並顯示正常

## 📝 腳本演進歷史

### 版本 1: 原始版本 (simulate_compass_interference.py)
```python
CONNECTION_STRING = 'udp:127.0.0.1:14550'
update_interval = 1.0  # 每秒更新
steps = 20  # 20 個步驟
```

**問題**: 
- 更新太頻繁 (每秒 3 個參數 × 20 步 = 60 次/秒)
- QGC 斷線

### 版本 2: 優化版本
```python
CONNECTION_STRING = 'udp:127.0.0.1:14550'
update_interval = 2.0  # 每 2 秒更新
param_set_delay = 0.1  # 每個參數後延遲 0.1 秒
```

**改進**:
- 降低更新頻率到 0.5 次/秒
- 添加參數設定延遲

**問題**: 仍可能與 QGC 衝突

### 版本 3: 安全版本 (safe_compass_interference.py)
```python
# 最初版本
CONNECTION_STRING = 'udp:127.0.0.1:14551'  # 避開 QGC
update_rate = 0.5  # 2Hz
```

**問題**: 無法連接,卡在等待 Heartbeat

```python
# 修改後版本
CONNECTION_STRING = 'udp:127.0.0.1:14550'  # 改回 14550
```

**問題**: SITL 斷線

## 🤔 核心疑問

### Q1: ArduPilot SITL 的正確連接端口是什麼?
- 14550? (QGC 使用)
- 14551? (MAVROS 使用)
- 其他?

### Q2: 如何在不影響 QGC 的情況下發送參數?
- 使用不同的端口?
- 降低發送頻率?
- 使用不同的 MAVLink 連接方式?

### Q3: 為什麼 Port 14551 沒有 Heartbeat?
```bash
# Port 14551 確實在監聽
udp   0.0.0.0:14551   (多個實例)
```
但 Python 腳本連接後收不到 Heartbeat

## 📊 參數設定方式

### 當前使用的方法
```python
def set_param(mav, param_name, param_value, delay=0.1):
    mav.mav.param_set_send(
        mav.target_system,
        mav.target_component,
        param_name.encode('utf-8'),
        param_value,
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32
    )
    time.sleep(delay)
```

### 參數名稱
```python
PARAM_MAG_MOT_X = b'SIM_MAG_MOT_X'
PARAM_MAG_MOT_Y = b'SIM_MAG_MOT_Y'
PARAM_MAG_MOT_Z = b'SIM_MAG_MOT_Z'
```

## 🎯 期望行為

1. Python 腳本連接到 SITL
2. QGC 保持連線 (不斷線)
3. 腳本動態改變 SIM_MAG_MOT_X/Y/Z 參數
4. 能在 QGC 中觀察到磁力計數值變化
5. 出現 "Compass Unhealthy" 警告
6. 腳本結束後自動重置參數

## 📁 相關文件

### 完整腳本代碼
請查看附件:
- `simulate_compass_interference.py` (優化版)
- `safe_compass_interference.py` (安全版)

### 關鍵代碼片段

#### 連接邏輯
```python
CONNECTION_STRING = 'udp:127.0.0.1:14550'  # 或 14551?
master = mavutil.mavlink_connection(CONNECTION_STRING)
master.wait_heartbeat()  # 這裡卡住或超時
```

#### 參數更新循環
```python
while True:
    elapsed = time.time() - start_time
    if elapsed > total_duration:
        break
    
    # 計算磁場強度
    current_strength = calculate_strength(elapsed)
    mag_mot = calculate_mag_mot(current_strength)
    
    # 設定參數
    set_param(master, PARAM_MAG_MOT_X, mag_mot)
    set_param(master, PARAM_MAG_MOT_Y, mag_mot * 0.8)
    set_param(master, PARAM_MAG_MOT_Z, mag_mot * 1.2)
    
    time.sleep(update_rate)  # 0.5 秒
```

## 🆘 需要幫助的問題

1. **ArduPilot SITL 的正確 MAVLink 連接方式是什麼?**
   - 應該用哪個端口?
   - 如何避免與 QGC 衝突?

2. **為什麼改用 14550 會導致 SITL 斷線?**
   - 是 Port 衝突嗎?
   - 還是參數發送方式有問題?

3. **有沒有更好的方式動態改變 SITL 參數?**
   - MAVProxy 腳本?
   - 其他 MAVLink 工具?

4. **如何實現多客戶端連接?**
   - QGC 連接 14550
   - Python 腳本連接 ???
   - 兩者互不干擾

## 🔍 已嘗試的解決方案

### ❌ 方案 1: 降低更新頻率
- 從 1.3 次/秒降到 0.5 次/秒
- 結果: 仍然斷線

### ❌ 方案 2: 使用 Port 14551
- 避開 QGC 的 14550
- 結果: 無法收到 Heartbeat

### ❌ 方案 3: 改回 Port 14550
- 直接連接主端口
- 結果: SITL 斷線

### ⏳ 方案 4: 待嘗試
- 使用 MAVProxy 的 `module load` 功能?
- 使用 MAVROS 作為中介?
- 其他?

## 📚 參考資料

- ArduPilot SITL 文檔: https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html
- MAVLink 協議: https://mavlink.io/
- pymavlink 文檔: https://mavlink.io/en/mavgen_python/

---

**請幫助我找出正確的連接方式,讓 Python 腳本能在不影響 QGC 的情況下動態改變 SITL 參數。謝謝!**
