# Jetson AIoT "Sentient Hub" Project Roadmap

這份計畫是為您的硬體量身打造的。我們將利用這些感測器與 ESP32 CAM，構建一個 **「具備感知能力的 AIoT 中樞 (Sentient Hub)」**。

這個專案將帶您走過您在 README 中整理的所有層級：
*   **Layer 1 HW**: 連接感測器 (IMU, PX4, OLED).
*   **Layer 2 Kernel**: 設定 I2C/PWM 驅動.
*   **Layer 3 Middleware**: 使用 Docker 封裝環境.
*   **Layer 4 Framework**: 使用 Flask + OpenCV 處理 ESP32 CAM 串流.
*   **Layer 5 Application**: 接上 LLM (Gemini)，讓它能「讀懂」感測器數據並「開口說話」(Speaker).

## 硬體角色分配 (Hardware Roles)

| 硬體 | 角色 | 連接介面 | 用途 |
| :--- | :--- | :--- | :--- |
| **Jetson Nano** | **大腦 (Brain)** | N/A | 運算核心、Docker Host、LLM 執行者。 |
| **ESP32 CAM** | **眼睛 (Remote Eye)** | **Wi-Fi** | Nano 沒有 USB Cam，但我們可以用 ESP32 CAM 架設 MJPEG/RTSP Server，讓 Nano 透過網路抓取影像進行 AI 分析。 |
| **IMU (MPU6050)** | **內耳 (Balance)** | I2C | 偵測震動、傾斜。可用來觸發警報 (如地震偵測)。 |
| **OLED (SSD1306)** | **臉部 (Face)** | I2C | 顯示系統狀態、IP、或 LLM 的心情表情 (O_O, ^_^)。 |
| **Servo (SG90)** | **脖子 (Neck)** | PWM (GPIO) | 讓 ESP32 CAM 可以左右轉動。 |
| **Joystick** | **神經傳導 (Input)** | GPIO/ADC | 手動控制介面。 |
| **Speaker** | **嘴巴 (Mouth)** | Audio Jack | 讓 LLM 將回應轉為語音 (TTS)。 |
| **PX4** | **外骨骼 (Ext. System)** | UART/USB | (進階) 讀取更精密的飛行姿態數據。 |

---

## 階段性任務 (Milestones)

### Phase 1: 神經連結 (Hardware & Kernel Layer)
**目標**：不使用 Docker，先在 Nano 本機上用 Python 腳本成功控制所有 I/O。
1.  **I2C 檢測**：確認 `i2cdetect -y 1` 能抓到 IMU 和 OLED。
2.  **GPIO 控制**：寫 Python 讓 Joystick 控制 Servo 轉動。
3.  **OLED 顯示**：在 OLED 上顯示 Hello World。

### Phase 2: 移植視神經 (Network Layer)
**目標**：讓 Jetson 看到 ESP32 CAM 的畫面。
1.  **ESP32 端**：燒錄 CameraWebServer 範例程式，確保它在區域網路內能串流影像 (http://192.168.x.x/stream)。
2.  **Jetson 端**：寫一個 Python OpenCV script (`cv2.VideoCapture`) 讀取該 URL 並顯示畫面。

### Phase 3: 軀體封裝 (Docker Middleware Layer)
**目標**：將上述環境打包進 Docker，這是 Jetson 開發最重要的一環。
1.  **Dockerfile 撰寫**：基於 `l4t-ml` 或 `python:slim`，安裝 `RPI.GPIO`, `smbus` (I2C用), `opencv-python`。
2.  **硬體透傳**：學習如何在 `docker run` 時使用 `--device /dev/i2c-1` 和 `--privileged` 讓容器能控制硬體。

### Phase 4: 注入靈魂 (Application & AI Layer)
**目標**：整合 Flask 與 LLM，打造互動介面。
1.  **Flask Dashboard**：網頁上顯示 ESP32 CAM 即時畫面、IMU 數值波形圖。
2.  **LLM Agent**：
    *   **情境 A (監控)**：當 IMU 偵測到劇烈晃動 -> LLM 判斷 "Earthquake?" -> 控制 Speaker 發出警報 -> 控制 OLED 顯示 "WARNING"。
    *   **情境 B (視覺)**：每 5 秒擷取 ESP32 CAM 畫面 -> 傳給 Gemini Vision -> Gemini 回傳 "我看見一個人" -> OLED 顯示文字。

---
