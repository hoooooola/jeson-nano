#!/usr/bin/python
# -*- coding: utf-8 -*-


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


# 匯入 RPi.GPIO 模組以控制 Raspberry Pi 的 GPIO
import RPi.GPIO as GPIO
# 匯入 time 模組用於延遲操作
import time

# 定義每個板子的 PWM 輸出引腳
output_pins = {
    'JETSON_XAVIER': 18,          # 對應 Jetson Xavier 的 PWM 引腳
    'JETSON_NANO': 33,           # 對應 Jetson Nano 的 PWM 引腳
    'JETSON_NX': 33,             # 對應 Jetson NX 的 PWM 引腳
    'CLARA_AGX_XAVIER': 18,      # 對應 Clara AGX Xavier 的 PWM 引腳
    'JETSON_TX2_NX': 32,         # 對應 Jetson TX2 NX 的 PWM 引腳
    'JETSON_ORIN': 18,           # 對應 Jetson Orin 的 PWM 引腳
}

# 根據目前板子的型號取得對應的 PWM 引腳
output_pin = output_pins.get(GPIO.model, None)
# 如果找不到支援的 PWM 引腳則拋出例外
if output_pin is None:
    raise Exception(' no support PWM')

# 主程式入口點
def main():
    # 引腳設置：
    # 使用 BOARD 編號方式
    GPIO.setmode(GPIO.BOARD)
    # 設置指定的引腳為輸出引腳，並且初始狀態為高電平
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    # 建立 PWM 物件，頻率為 50Hz（適用於伺服馬達）
    servo = GPIO.PWM(output_pin, 50)
    # 啟動 PWM，初始占空比為 0（馬達不動）
    servo.start(0)

    print ("Rotating at intervals of 12 degrees")  # 以 12 度為間隔旋轉伺服馬達 # 提示用戶程序的功能
    duty = 2  # 初始占空比，對應伺服馬達的最小角度（約 0 度）

    try:
        while duty <= 17:  # 占空比範圍從 2 到 17，對應 0 到 180 度
            servo.ChangeDutyCycle(duty)  # 改變占空比以控制馬達角度
            time.sleep(1)  # 延遲 1 秒以穩定伺服馬達的動作
            duty += 1      # 每次增加 1 的占空比
    finally:
        servo.stop()  # 停止 PWM
        GPIO.cleanup()  # 清理 GPIO 設定，確保釋放資源

# 判斷是否是從主程式執行
if __name__ == '__main__':
    main()  # 呼叫主函式


