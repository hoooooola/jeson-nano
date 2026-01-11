# 歷史檔案資料夾 (History Folder - Ignore)

此資料夾包含已被新版本取代或不再使用的檔案,保留作為歷史參考。

## 📁 檔案清單

### 已廢棄的啟動腳本
- **`run_sim.sh`** (907 bytes)
  - 舊版容器啟動腳本
  - 使用 `docker run` 直接啟動,已被 `docker-compose` 取代
  - 包含 `--privileged` 模式(安全性問題)
  - **取代者**: `launch_all.sh` + `docker-compose.yml`

- **`setup_ardupilot.sh`** (914 bytes)
  - 手動設置 ArduPilot 的腳本
  - 功能已整合到 Dockerfile 中
  - **取代者**: Dockerfile 第 59-66 行

- **`install_qgc.sh`** (445 bytes)
  - QGroundControl 手動下載指南
  - 已不需要,QGC 直接使用 AppImage
  - **取代者**: 直接執行 `QGroundControl-x86_64.AppImage`

### 測試產生的臨時檔案
- **`mav.parm`** (30 KB) - SITL 參數檔案
- **`mav.tlog`** (3.2 MB) - MAVLink 遙測日誌
- **`mav.tlog.raw`** (2.5 MB) - 原始遙測數據
- **`eeprom.bin`** (16 KB) - 模擬 EEPROM 數據

> 這些檔案會在每次執行 SITL 時自動重新生成

### 其他
- **`QGroundControl.AppImage`** (0 bytes) - 空檔案,下載失敗的殘留
- **`image.png`** (1.2 MB) - 測試截圖

## 🗑️ 清理建議

如果確認不再需要這些檔案,可以安全刪除整個資料夾:

```bash
rm -rf histryFolderIgnore
```

## 📊 空間節省

移動這些檔案後,主目錄從 **180MB** 減少到 **173MB**,節省約 **6.8MB**。

---

**移動日期**: 2026-01-11  
**原因**: 整理專案結構,保持主目錄簡潔
