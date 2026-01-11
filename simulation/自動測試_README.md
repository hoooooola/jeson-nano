# 自動化磁力計干擾測試 - 快速參考

## 🚀 一鍵啟動

```bash
# 1. 啟動 SITL 環境
./launch_all.sh

# 2. 在新終端執行測試
python3 auto_compass_interference_test.py
```

## 📋 測試內容

1. **磁力計參數歸零** - 自動重置所有校正參數
2. **自動起飛** - GUIDED mode → ARM → TAKEOFF 20m
3. **POI 繞圓** - 半徑 5m, 速度 2 m/s, 持續 75 秒
4. **高強度干擾** - 磁場強度從 1.0x 漸增到 5.0x

## 🎯 預期結果

- ✅ 無人機自動起飛到 20m
- ✅ 在 Gazebo 中看到圓形飛行軌跡
- ✅ QGC 顯示磁力計警告
- ✅ 飛行模式可能切換到 ALT_HOLD 或 LAND

## ⚠️ 注意事項

- 僅適用於 SITL 模擬環境
- 按 `Ctrl+C` 可隨時停止測試
- 測試完成後需手動降落: `mode LAND`

## 📚 詳細文檔

- [完整使用指南](測試使用指南.md)
- [實現計劃](implementation_plan.md)
- [原始干擾腳本](production_compass_interference.py)

## 🔧 調整參數

編輯 `auto_compass_interference_test.py`:

```python
# 飛行參數
TAKEOFF_ALTITUDE = 20.0  # 起飛高度
CIRCLE_RADIUS = 5.0      # 繞圓半徑
CIRCLE_SPEED = 2.0       # 繞圓速度

# 干擾強度
'critical_strength': 5.0  # 最大干擾倍數
'base_offset': 3000       # 基礎偏移 (mGauss)
```

## 🐛 常見問題

**Q: 連線失敗?**
A: 確認 SITL 已啟動,檢查 `netstat -tuln | grep 5762`

**Q: 解鎖失敗?**
A: 在 MAVProxy 中執行 `arm throttle force`

**Q: 無人機不繞圓?**
A: 檢查 `param show SYSID_MYGCS`,應為 255

**Q: 干擾無效果?**
A: 檢查 `param show SIM_MAG1_OFS_*`,應該在干擾時不為 0
