#!/usr/bin/python
# -*- coding: utf-8 -*-

#!/usr/bin/env python

# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
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

# 定義引腳
input_pin = 18  # 使用 BCM 模式的引腳 18，對應於 BOARD 模式的引腳 12

# 主程式入口點
def main():
    prev_value = None  # 初始化上一個引腳值為 None

    # 引腳設定：
    GPIO.setmode(GPIO.BCM)  # 設定 GPIO 模式為 BCM 模式
    GPIO.setup(input_pin, GPIO.IN)  # 將指定引腳設為輸入模式
    print("Starting demo now! Press CTRL+C to exit")  # 提示使用者程式開始執行

    try:
        while True:
            value = GPIO.input(input_pin)  # 讀取輸入引腳的值
            if value != prev_value:  # 如果引腳值與之前的值不同
                if value == GPIO.HIGH:  # 如果值為高電平
                    value_str = "HIGH"  # 設定為 "HIGH"
                else:
                    value_str = "LOW"  # 否則設定為 "LOW"
                # 輸出讀取到的值
                print("Value read from pin {} : {}".format(input_pin,
                                                           value_str))
                prev_value = value  # 更新上一個引腳值
            time.sleep(1)  # 延遲 1 秒以降低處理頻率
    finally:
        GPIO.cleanup()  # 清理 GPIO 設定，確保程式結束時引腳處於安全狀態

# 判斷是否是從主程式執行
if __name__ == '__main__':
    main()  # 呼叫主函式
