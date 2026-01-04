#!/usr/bin/python
# -*- coding: utf-8 -*-

# 匯入 smbus2 模組
from smbus2 import SMBus

# 設定 ADS1115 的 I2C 地址
I2C_ADDRESS = 0x48  # 默認 I2C 地址
I2C_BUS = 1         # Jetson Nano 默認使用 I2C bus 1

# ADS1115 的寄存器地址
REG_CONVERSION = 0x00  # 轉換數據寄存器
REG_CONFIG = 0x01      # 配置寄存器

# 配置參數
# 單端 A0 通道，FS=±4.096V，128 SPS
CONFIG = [
    0xC1,  # MSB: AIN0 單端, FSR ±4.096V, 單次模式
    0x83   # LSB: 128 SPS, 禁用比較器
]

# 初始化 I2C
with SMBus(I2C_BUS) as bus:
    # 寫入配置寄存器
    bus.write_i2c_block_data(I2C_ADDRESS, REG_CONFIG, CONFIG)

    # 等待測量完成（單次模式）
    import time
    time.sleep(0.01)  # ADS1115 需要一些時間完成測量

    # 讀取轉換寄存器中的數據（2 bytes）
    data = bus.read_i2c_block_data(I2C_ADDRESS, REG_CONVERSION, 2)

# 將數據轉換為整數
raw_adc = (data[0] << 8) | data[1]
if raw_adc > 0x7FFF:  # 處理負數
    raw_adc -= 0x10000

# 計算實際電壓（FSR = ±4.096V，分辨率 = 32768）
voltage = raw_adc * 4.096 / 32768.0

# 輸出結果
print(f"A0 原始數據: {raw_adc}")
print(f"A0 電壓: {voltage:.3f} V")
