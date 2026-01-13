# Gazebo Harmonic + ArduPilot Plugin Timing Review

## 問題本質

ArduPilot Gazebo Plugin 對**模擬時間連續性**非常敏感：

```
Render thread / physics thread block
         ↓
Real-time factor (RTF) 掉到 0
         ↓
Gazebo 重置 sim clock
         ↓
Plugin 偵測 controller reset
         ↓
SITL heartbeat 中斷
```

**GPU 初始化失敗是最常見的上游 trigger。**

---

## 核心 Timing 原則（實務）

### 1️⃣ Gazebo 與 SITL 一定要拆 container

| 元件 | 特性 | 為什麼獨立 |
|------|------|-----------|
| Gazebo | GPU / EGL / X11 | 渲染抖動會影響 sim clock |
| SITL | CPU / timing | 需要穩定的時間來源 |

混在一起 = render hiccup → SITL reset

### 2️⃣ Gazebo 啟動參數

```bash
gz sim -r -v4 iris_runway.sdf
```

- `-r`：lock real-time，避免無限制 RTF 飄移

### 3️⃣ ArduPilot SITL 建議參數

```bash
sim_vehicle.py -v ArduCopter \
  --model JSON \
  --speedup 1 \
  --no-mavproxy
```

- `speedup > 1` 在 GPU 抖動時容易炸
- MAVProxy 獨立 container

### 4️⃣ Plugin reset 的真正意義

```
[Wrn] ArduPilot controller has reset
```

- ≠ firmware crash
- = Gazebo time discontinuity

---

## 建議 Debug 順序（永遠照這個）

1. `sim-doctor` GPU 檢查
2. Gazebo RTF 是否穩定
3. SITL port 5760
4. MAVProxy heartbeat
5. QGC

---

## 一句最終工程總結

> **Gazebo + ArduPilot 的穩定性，決定於 GPU 與時間來源的可預測性，而不是 MAVLink 本身。**
