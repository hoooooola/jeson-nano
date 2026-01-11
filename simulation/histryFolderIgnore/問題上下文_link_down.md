# ArduPilot SITL 磁力計干擾模擬 - 完整上下文 (給 DeepSeek)

## 🎯 目標

在 ArduPilot SITL 環境中實現動態磁力計干擾模擬,用於飛行員應急訓練。模擬真實案例:磁場強度從 0.75 逐漸上升到 2.0,導致飛行器進入姿態模式。

## 📊 當前狀態

### ✅ 已解決的問題

1. **QGC 斷線** - 改用 TCP 5762 (開發者端口)
2. **參數無效** - 改用 SIM_MAG1_OFS_* (直接偏移)
3. **GPU 權限** - Docker 已配置 /dev/dri 直通

### ✅ 系統正常運行

```
TCP 端口:
- 5760 ✅ LISTEN
- 5762 ✅ LISTEN (腳本使用)
- 5763 ✅ LISTEN

UDP 端口:
- 14550 ✅ (QGC)

SITL 狀態:
- JSON 通訊正常
- 參數已加載
- 飛控已啟動
```

### ⚠️ 當前觀察

MAVProxy 顯示 "link 1 down",但其他連接正常。

## 🔍 需要確認的問題

### 問題: "link 1 down" 是否正常?

**上下文**:
- MAVProxy 同時監聽多個端口 (5760, 5762, 5763, 14550)
- 顯示 "link 1 down" 但其他功能正常
- SITL 仍在接收 JSON 數據
- 所有端口都在 LISTEN 狀態

**疑問**:
1. "link 1 down" 是否影響磁力計干擾模擬?
2. 是否需要修復?還是可以忽略?
3. 如果需要修復,應該如何處理?

## 📁 相關配置

### MAVProxy 啟動方式

```bash
# 在 start_sitl.sh 中
cd ardupilot/ArduCopter
../Tools/autotest/sim_vehicle.py -v ArduCopter -f JSON --console --map
```

這會自動啟動 MAVProxy 並綁定多個端口。

### Python 腳本連接方式

```python
# production_compass_interference.py
CONNECTION_STRING = 'tcp:127.0.0.1:5762'
SOURCE_SYSTEM = 254  # Secondary GCS

master = mavutil.mavlink_connection(
    CONNECTION_STRING,
    source_system=SOURCE_SYSTEM
)
```

### Docker 網路配置

```yaml
# docker-compose.yml
services:
  sitl:
    network_mode: host  # 使用主機網路
    devices:
      - /dev/dri:/dev/dri
```

## 🎯 預期行為

### 正常情況應該是:

1. MAVProxy 啟動並綁定所有端口
2. QGC 連接到 14550
3. Python 腳本連接到 5762
4. 所有連接保持穩定

### 當前情況:

1. ✅ MAVProxy 已啟動
2. ✅ 端口都在監聽
3. ✅ SITL 正常運行
4. ⚠️ 顯示 "link 1 down"

## 📊 MAVLink 連接架構

```
SITL (ArduCopter)
    ↓
MAVProxy (Hub)
    ├─ TCP 5760 → 開發者端口 1
    ├─ TCP 5762 → 開發者端口 2 (Python 腳本)
    ├─ TCP 5763 → 開發者端口 3
    └─ UDP 14550 → QGC

當前狀態:
- link 0: ✅ (主連接)
- link 1: ❌ down
- link 2-3: ? (未知)
```

## 🔧 可能的原因

### 假設 1: 正常行為
- MAVProxy 預設會嘗試連接多個端口
- 某些端口沒有客戶端連接時顯示 "down"
- 不影響實際功能

### 假設 2: 配置問題
- MAVProxy 配置了額外的輸出端口
- 但沒有對應的客戶端連接
- 需要調整 MAVProxy 配置

### 假設 3: 競爭條件
- 多個服務同時啟動
- 某個連接建立失敗
- 需要調整啟動順序或延遲

## 📝 相關日誌

### SITL 啟動日誌 (正常部分)

```
Starting SITL input
Using Irlock at port : 9005
bind port 5760 for SERIAL0
SERIAL0 on TCP port 5760
bind port 5762 for SERIAL1
SERIAL1 on TCP port 5762
bind port 5763 for SERIAL2
SERIAL2 on TCP port 5763

JSON received:
    timestamp
    imu: gyro
    imu: accel_body
    position
    quaternion
    velocity
```

### MAVProxy 控制台

```
UNKNOWN    ARM   GPS: --    Vcc: --   Radio: --
Hdg --/--  Alt --  AGL --/--  AirSpeed --
WP --  Distance --  Bearing --  AltError --
link 1 down
```

## ❓ 具體問題

1. **"link 1 down" 的含義是什麼?**
   - 是哪個連接斷開了?
   - 為什麼會斷開?

2. **是否影響功能?**
   - 磁力計干擾模擬是否會受影響?
   - QGC 連接是否正常?

3. **如何修復?**
   - 需要修改 MAVProxy 配置嗎?
   - 需要調整啟動腳本嗎?
   - 還是可以安全忽略?

4. **如何驗證?**
   - 如何確認所有連接都正常?
   - 有什麼診斷指令可以用?

## 🎯 期望的回答

1. 解釋 "link 1 down" 的具體含義
2. 判斷是否需要修復
3. 如果需要修復,提供具體步驟
4. 如果可以忽略,說明原因

## 📚 參考資料

- ArduPilot SITL 文檔: https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html
- MAVProxy 文檔: https://ardupilot.org/mavproxy/
- MAVLink 協議: https://mavlink.io/

---

**環境信息**:
- OS: Ubuntu 22.04
- Docker: 使用 host 網路模式
- ArduPilot: 最新版 (從 GitHub clone)
- MAVProxy: 隨 sim_vehicle.py 自動啟動
- Gazebo: Harmonic

**當前任務**: 準備執行磁力計干擾模擬,但想先確認 "link 1 down" 是否會影響測試。
