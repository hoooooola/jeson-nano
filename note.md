[info](https://drive.google.com/drive/folders/12ziUuyp-AXPtEMNotsjHQ_TJ5xlohHLQ)

[FPGA](https://drive.google.com/drive/folders/12ziUuyp-AXPtEMNotsjHQ_TJ5xlohHLQ)

## Nvidia Jetson Ecosystem
- Linux OS + 平行運算 + 容器化部署
- 挑戰在於「如何將 AI 模型高效地部署在邊緣端（Edge）並與硬體互動」
### HW
- 

### SW
這份內容非常有條理，非常適合整理成 Markdown 筆記格式。以下是轉換後的版本，增加了標題層級、粗體強調與表格，以提升閱讀體驗。

***

### 1. 核心基石：JetPack SDK (The Foundation)

這是所有 Jetson 開發的基礎。你可以把它想像成 Jetson 的「作業系統 + 驅動 + 加速庫」的大禮包

*   **OS (L4T - Linux for Tegra):** 基於 Ubuntu 的客製化 Linux 系統。這就是為什麼你會看到 Ubuntu 桌面環境。
*   **CUDA & cuDNN:** GPU 加速的核心。整合GPU, CPU, parallel compute and serial compute.
*   **TensorRT (關鍵):** 開發者必學。這是 NVIDIA 最強的推論（Inference）引擎。它負責將你訓練好的模型（來自 PyTorch/TensorFlow）進行「最佳化（Quantization, Layer Fusion）」，讓模型在 Jetson 上跑得飛快（FPS 提升數倍）。
*   **Multimedia API:** 硬體編解碼（Hardware Codec），處理 H.264/H.265 影片串流，減輕 CPU 負擔。

> **💡 開發者筆記：**
> 剛開始你會直接用 PyTorch 跑模型，但為了效能（Performance），最終你一定會需要學會如何將模型轉檔為 TensorRT engine (`.plan`)。

---

### 2. 機器人與自主移動：Isaac & ROS (The Brain & Body)

針對你提到的 FSD (Full Self-Driving 概念)、SLAM 和 ROS，這是目前的標準路徑：

*   **ROS / ROS 2 (Robot Operating System):** 機器人開發的通訊標準。Jetson 完美支援 ROS 2 (Humble/Foxy 等版本)。
*   **Docker 的角色：** 現在主流開發都建議直接在 Jetson 上跑 **ROS 2 Docker Container**，避免環境汙染。
*   **NVIDIA Isaac ROS (硬體加速版 ROS):** 這是 NVIDIA 推出的 ROS 2 軟體包（GEMs）。它將標準的 ROS 節點（Node）用 GPU 加速。

**應用場景：**
*   **vSLAM (Visual SLAM):** 使用 Isaac ROS Visual SLAM package，直接用 GPU 算位置。
*   **AprilTag:** 視覺標籤識別加速。
*   **NvBlox:** 建立 3D 避障地圖。

---

### 3. 智慧影像分析：DeepStream & Vision (The Eyes)

如果你要做「影像識別」、「監控 Server」或「多路影像分析」，光靠 OpenCV 是不夠的。

*   **DeepStream SDK:**
    *   **用途：** 專門處理多路（Multi-stream）影片分析的流水線（Pipeline）。
    *   **優勢：** 資料從 `攝影機` -> `解碼` -> `預處理` -> `AI 推論` -> `繪圖` -> `輸出`，全程都在 GPU 記憶體中完成 (**Zero Copy**)，CPU 幾乎不介入。
    *   **應用：** 智慧城市監控、工廠瑕疵檢測、車牌辨識 (LPR)。
*   **OpenCV (VPI - Vision Programming Interface):** Jetson 上有 VPI，這是 NVIDIA 版本的 OpenCV 加速庫，專門用來做傳統電腦視覺（邊緣檢測、縮放、變形）的 GPU 加速。

---

### 4. 快速上手與模型訓練 (The Workflow)

你提到的「20 個範例, 不到 20 行 CODE」通常是指 "Hello AI World" (Jetson Inference) 專案。

*   **Hello AI World (Jetson Inference):**
    *   這是最適合初學者的開源專案。
    *   內建 ImageNet (分類), DetectNet (物件偵測), SegNet (分割) 的範例。
    *   確實只需要極少的 Python code 就能跑起即時影像辨識。
*   **NVIDIA TAO Toolkit (Train - Adapt - Optimize):**
    *   如果你不想從零開始寫 AI 模型，可以使用 TAO。
    *   它提供預訓練模型（Pre-trained Models，如車牌辨識、人臉偵測），你只需要準備少量資料做 **Transfer Learning (遷移學習)** 即可。

---

### 總結：開發者技術地圖 (Tech Stack Summary)

為了達成你提到的應用，你的技術堆疊通常會長這樣：

| 層級 | 關鍵組件 | 開發者會碰到的事 |
| :--- | :--- | :--- |
| **Application** | FSD / SLAM / Server | 撰寫 Python/C++ 邏輯，整合感知數據。 |
| **Middleware** | Isaac ROS / DeepStream | 使用現成的 GPU 加速節點 (Node) 或 插件 (Plugin)。 |
| **Framework** | ROS 2 / Docker | 管理容器環境，處理節點間通訊。 |
| **Inference** | TensorRT | 將 `.pt` / `.onnx` 模型轉為 `.engine` 以獲得最高 FPS。 |
| **OS / Driver** | JetPack (L4T) | 刷機 (Flash OS)、監控 GPU 溫度與負載 (`jtop`)。 |



### Application
- server
- 影像識別
- FSD, SLAM

# Edge AI
- Edge device (SOM+AI model)
- Edge computing (arm5 mcu 單晶片+tf lite)
## edge device
- JAX/ TF/ Torch
- jeson, ubuntu
- tf lite
- python
## edge computing
- arm5 m5, m55, m6
- hal, 底層使用tf 使用hal 打包
- 

# NVIDIA JetPack

## 概述
JetPack SDK = 作業系統 + 驅動 + 加速庫 (基於 Ubuntu OS)

## 核心組件

### 1. OS (L4T - Linux for Tegra)
- 基於 Ubuntu 的客製化 Linux 系統
- 這就是為什麼你會看到 Ubuntu 桌面環境

### 2. CUDA & cuDNN
- GPU 加速的核心
- 沒有它們,Jetson 就只是一塊普通的 ARM 板子

### 3. TensorRT ⭐ (關鍵)
- **開發者必學**
- NVIDIA 最強的推論 (Inference) 引擎
- 功能:
  - 將訓練好的模型 (來自 PyTorch/TensorFlow) 進行最佳化
  - 執行 Quantization、Layer Fusion 等優化技術
  - 讓模型在 Jetson 上跑得飛快 (FPS 提升數倍)

### 4. Multimedia API
- 硬體編解碼 (Hardware Codec)
- 處理 H.264/H.265 影片串流
- 減輕 CPU 負擔

### 5. 其他工具
- OpenCV, OpenALPR, OpenSTAMINA

## 開發者筆記
> 💡 剛開始你會直接用 PyTorch 跑模型,但為了效能 (Performance),最終你一定會需要學會如何將模型轉檔為 TensorRT engine (`.plan`)。

## 資源
- 20+ 個範例,不到 20 行 CODE
- [官方文件](https://developer.nvidia.com/embedded/jetpack)

# https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#intro


