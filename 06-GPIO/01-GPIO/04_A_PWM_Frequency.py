#!/usr/bin/python
# -*- coding: utf-8 -*-

#!/usr/bin/env python

# Copyright (c) 2019-2020, NVIDIA CORPORATION. All rights reserved.
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


# 匯入 RPi.GPIO 模組來控制 Raspberry Pi 的 GPIO
import RPi.GPIO as GPIO
# 匯入 time 模組以便使用延遲功能
import time

# 定義不同 Jetson 板子的 PWM 輸出引腳
output_pins = {
    'JETSON_XAVIER': 18,          # Jetson Xavier 的 PWM 引腳為 BCM 18
    'JETSON_NANO': 33,            # Jetson Nano 的 PWM 引腳為 BOARD 33
    'JETSON_NX': 33,              # Jetson NX 的 PWM 引腳為 BOARD 33
    'CLARA_AGX_XAVIER': 18,       # Clara AGX Xavier 的 PWM 引腳為 BCM 18
    'JETSON_TX2_NX': 32,          # Jetson TX2 NX 的 PWM 引腳為 BOARD 32
    'JETSON_ORIN': 18,            # Jetson Orin 的 PWM 引腳為 BCM 18
}

#Jetson 的 PWM 硬體可能要求頻率值必須在特定範圍內，
# 例如某些板子可能只支持特定範圍（如 50 Hz 到 1000 Hz）。



# 根據 GPIO 的板型設定對應的 PWM 引腳
output_pin = output_pins.get(GPIO.model, None)  # 取得當前板子對應的引腳
if output_pin is None:  # 如果找不到對應引腳，拋出異常
    raise Exception('PWM not supported on this board')  # 此板子不支援 PWM

# 主程式函式
def main():
    # 引腳設定
    GPIO.setmode(GPIO.BOARD)  # 設定為 BOARD 編號模式
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)  # 將指定引腳設為輸出模式，並初始為高電壓

    # PWM 設定，頻率為 50 Hz
    p = GPIO.PWM(output_pin, 50)  # 建立 PWM 物件，控制指定引腳
    # 使用 dir() 函數列出 PWM 支援的方法和屬性
    print("Available methods and attributes in PWM:")
    print(dir(p))
    # exit()

    
    val = 70  # 初始
    incr = 1  
    p.start(50)  # 啟動 PWM，使用初始佔空比
    print("PWM running. Press CTRL+C to exit.") # 提示使用者 PWM 已啟動

    try:
        while True:
            time.sleep(1)  # 每次循環延遲 1 秒
            if val >= 100:  # 如果佔空比達到 100%，反向減小
                incr = -incr
            if val <= 50:  # 如果佔空比達到 0%，反向增加
                incr = -incr
            val += incr  # 更新佔空比            
            print("val=",val,"incr=",incr)
            if val>0:
              p.ChangeFrequency(val)  # 設定新的頻率 ，調整 PWM 輸出
            else:
              print("val<0")  # 提示無效頻率值被忽略
    finally:
        p.stop()  # 停止 PWM
        GPIO.cleanup()  # 清理所有 GPIO 設定，確保程式結束時資源釋放

# 判斷是否從主程式執行
if __name__ == '__main__':
    main()  # 執行主程式




