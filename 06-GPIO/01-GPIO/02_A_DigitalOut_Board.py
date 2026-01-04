#!/usr/bin/python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO  # 匯入 RPi.GPIO 模組，用來控制樹莓派的 GPIO 引腳
import time              # 匯入 time 模組，用來實現時間延遲功能


output_pin = 12  # 定義輸出引腳，使用 BOARD 模式對應的腳位是第 12 腳


# 定義一個函數 做事情
def main():
    # 定義Pin 
    GPIO.setmode(GPIO.BOARD)  # 設定 GPIO 模式為 BOARD 模式（物理引腳編號）
    # 將指定 引腳12 設置為 輸出 引腳，初始狀態設定為 HIGH（高電位）
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)

    print("Starting demo now! Press CTRL+C to exit")  # 提示使用者程式已開始，按下 CTRL+C 退出
    curr_value=GPIO.HIGH#初始化當前輸出狀態為高電位
    try:
        while True:# 一直執行
            time.sleep(1)# 每次迴圈等待 1 秒
            # 每秒切換一次輸出狀態
            print("Outputting {} to pin {}".format(curr_value, output_pin))  # 打印當前輸出狀態
            GPIO.output(output_pin, curr_value)  # 將當前狀態輸出到指定引腳１２　
            curr_value ^= GPIO.HIGH  # 切換電平狀態（高電位和低電位切換）　^　相反　curr_value高低相反
    finally:
        GPIO.cleanup()# 清理所有 GPIO 設置，確保安全釋放資源


# 判斷 主程式 就執行
if __name__ == '__main__':
    main()  # 程式的入口點
