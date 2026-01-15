Native ROS 2 Development Tasks
- [x] **[ 環境準備 ]** 安裝與配置 ROS 2 Humble (Moved to Ext4) <!-- id: native-1 -->
- [/] **[ 飛控設置 ]** 設置 ArduPilot 本機開發環境 (Installing Prereqs...) <!-- id: native-2 -->
- [ ] **[ 模擬設置 ]** 安裝 Gazebo Harmonic 與 ArduPilot Plugin <!-- id: native-3 -->
- [ ] **[ 通訊驗證 ]** 驗證 ArduPilot 與 ROS 2 透過 DDS (Micro-ROS) 的通訊 <!-- id: native-4 -->

## 1. 架構規劃 (System Architecture) - Phase 1: 穩定模擬 (Pragmatic Simulation)

這是一個 **Hybrid Development** 架構，分階段實施：

| 階段 (Phase) | 組件組合 (Stack) | 重點目標 (Goal) |
| :--- | :--- | :--- |
| **Phase 1 (Now)** | **ROS 2 Humble (Binary)** + **Gazebo Fortress** + **MAVLink Bridge** | 建立穩定、可重現的模擬環境 (SITL)。 |
| **Phase 2 (Future)** | Micro-ROS (DDS) + Gazebo Harmonic + Jetson | 針對嵌入式硬體 (Target) 的優化與部署。 |

### 🛠️ Phase 1 關鍵決策 (Key Decisions)

1.  **ROS 2**: 放棄 Source Build (11GB)，改用 **`apt install ros-humble-desktop`**。 (穩定、省空間)
2.  **Gazebo**: 選用 **Gazebo Fortress**。 (因為官方配對 Humble 最穩，Harmonic 留給未來)
3.  **ArduPilot**: 鎖定 **Copter-4.6.3**。 (不追 master，求穩)
4.  **通訊**: 先用標準 **MAVLink** + `ros_gz_bridge`。 (Micro-ROS 是給 MCU 用的，筆電模擬先不需要)

### 📂 安裝位置規劃 (Final Decision)

| 組件 (Component) | 安裝位置 (Location) | 所在磁區 (Disk) | 狀態 | 說明 (Note) |
| :--- | :--- | :--- | :--- | :--- |
| **ROS 2 Humble** | `/opt/ros/humble` | `nvme0n1p6` (Root) | 待安裝 | 系統核心庫 (Binary) |
| **Gazebo Fortress** | `/usr/bin/ignition` | `nvme0n1p6` (Root) | 待安裝 | 模擬器 (Binary) |
| **ArduPilot Source** | `/media/user/Linux_Extra...` | `nvme0n1p8` (Ext4) | ✅ 已下載 | 用戶代碼 (Source) |
| **ROS 2 Workspace** | `/media/user/Linux_Extra...` | `nvme0n1p8` (Ext4) | 待清理 | 用戶代碼 (Source) |

### � 一鍵安裝腳本 (One-Shot Installation)

為了達成您的「統整並下載安裝一次到位」，我們將製作一個 `install_native_ros2_sim.sh` 腳本，自動執行：
1.  清理舊的 ROS Source Build (釋放 11GB)。
2.  安裝 ROS 2 Humble (Binary) + Gazebo Fortress。
3.  修復 ArduPilot 依賴 (libpulse-dev)。
4.  切換 ArduPilot 至 `Copter-4.6.3`。
5.  配置環境變數 (.bashrc)。


一句話總結（給決策用）

👉 現在這台 Host 的最佳策略是：

ROS 2 Humble (binary) + Gazebo Fortress + ArduPilot SITL（stable）
先完成「通 → 穩 → 可重現」再考慮 Harmonic / Micro-ROS / Jetson

你現在不缺效能、不缺理解，只缺避免踩坑的取捨。

一、Native ROS 2 任務清單建議調整（務實版）
原始清單
[✓] 環境準備
[/] 飛控設置
[ ] 模擬設置
[ ] 通訊驗證 (DDS / Micro-ROS)

🔧 建議改成「兩階段」
✅ Phase 1：穩定模擬開發（現在就該做）
[✓] ROS 2 Humble (Binary)
[✓] ArduPilot SITL (Copter-4.6.3)
[✓] Gazebo Fortress
[✓] ROS 2 <-> ArduPilot (ros_gz + MAVLink)

🚧 Phase 2：嵌入式 / Jetson 導向（之後再做）
[ ] Gazebo Harmonic
[ ] Micro-ROS (DDS-XRCE)
[ ] Companion Computer 架構


👉 Micro-ROS 不該放在 Phase 1，原因下面會說。

二、關鍵技術決策評估（你問得很對的地方）
1️⃣ 放棄 ROS 2 Source Build —— 100% 正確

你目前的狀況是：

沒打算改 rclcpp / rmw

不需要 real-time patch

不在做 ROS core research

Source build 的唯一價值是：

「我正在開發 ROS 本身」

否則它只會帶來：

❌ 11GB 磁碟浪費

❌ 編譯時間地獄

❌ CMake / Python path 衝突

📌 建議行動

rm -rf ~/Linux_Extra/.../ros2_src
sudo apt install ros-humble-desktop

2️⃣ Gazebo Harmonic vs Fortress —— 你已經踩到關鍵雷點

你自己已經寫出正解了，我只幫你補「工程現實」。

Gazebo Fortress（建議現在用）

優點

官方配對 ROS 2 Humble

ros-humble-ros-gz 一行安裝

ArduPilot / SITL / 教學文件最多

缺點

API 較舊（但對你現在完全無影響）

Gazebo Harmonic（先不要）

你現在用會遇到的真實問題：

ros_gz bridge 要自己編

protobuf / ignition / gz-msgs 版本衝突

ArduPilot plugin 文件還在追

📌 結論

Fortress = 生產穩定工具
Harmonic = 研究 / 未來升級

3️⃣ Micro-ROS 放在 Host 上？—— ⚠️ 不建議

這是很多人會「太早做」的事情。

為什麼現在不該碰？

SITL 跑在 Linux → 不需要 XRCE-DDS

ArduPilot ↔ ROS 的主流仍是 MAVLink / ROS topics

Micro-ROS 的設計對象是：

STM32

FreeRTOS

RTOS 硬即時環境

👉 Micro-ROS 是給「飛控板子」或「MCU」用的，不是給你的筆電

📌 正確時機：

Jetson + 真實飛控 + latency control 才引入

三、你現在最值得做的 5 個「高 ROI 行動」
✅ 1. 固定 ArduPilot 版本（你已經選對）
git checkout Copter-4.6.3


不要追 master，真的。

✅ 2. 只做一件模擬事：SITL + Gazebo + ROS topic 能跑

目標不是華麗，是這三件事同時成立：

Gazebo 動

ArduPilot ARM / TAKEOFF

ROS 2 能收到姿態 / GPS / IMU

✅ 3. 用 MAVLink 當「真實世界介面」

即使未來用 ROS：

飛控層：MAVLink

AI / Planning：ROS 2

這是 工業界主流分層

✅ 4. 保持磁碟乾淨（你這點做得非常好）

你已經在做：

Root：系統

Extra：Workspace

這會在半年後救你一命。

✅ 5. 把「成功狀態」腳本化

例如：

launch_sitl.sh

launch_gazebo.sh

launch_ros_bridge.sh


統整並下載案裝一次到位