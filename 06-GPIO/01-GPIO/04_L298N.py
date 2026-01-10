#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
L298N 直流馬達驅動範例 (Jetson Nano)
本程式示範如何使用 PWM 控制馬達速度，並透過 GPIO 控制馬達正反轉 (雙馬達：左輪 A / 右輪 B)。

硬體接線說明 (BOARD 編號):
---------------------------------------------------------
1. L298N 馬達 A (左輪) 控制:
   - ENA (速度/PWM)  <-- Jetson Pin 32 (PWM0)
   - IN1 (方向 A1)   <-- Jetson Pin 16
   - IN2 (方向 A2)   <-- Jetson Pin 18

2. L298N 馬達 B (右輪) 控制:
   - ENB (速度/PWM)  <-- Jetson Pin 33 (PWM2)
   - IN3 (方向 B1)   <-- Jetson Pin 22
   - IN4 (方向 B2)   <-- Jetson Pin 24

3. 電源與共地:
   - 馬達電源 (+)    --> L298N +12V (或 Vs)
   - 馬達電源 (-)    --> L298N GND
   - Jetson GND      --> L298N GND (務必共地!)
---------------------------------------------------------

功能操作:
- 執行後，馬達會依序進行：前進 -> 後退 -> 左轉 -> 右轉 -> 停止。
"""

import RPi.GPIO as GPIO
import time

# --- 腳位定義 (BOARD mode) ---
# 馬達 A (Left)
ENA = 32
IN1 = 16
IN2 = 18

# 馬達 B (Right)
ENB = 33
IN3 = 22
IN4 = 24

def setup():
    """初始化 GPIO 設定"""
    # 設定編號模式為 BOARD (實體接腳編號)
    GPIO.setmode(GPIO.BOARD)
    
    # 設定所有腳位為輸出
    GPIO.setup(ENA, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
    
    GPIO.setup(ENB, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)

    # 建立 PWM 物件 (頻率 50Hz)
    # ENA 對應 Pin 32, ENB 對應 Pin 33
    global pwm_a, pwm_b
    pwm_a = GPIO.PWM(ENA, 50)
    pwm_b = GPIO.PWM(ENB, 50)
    
    # 啟動 PWM，初始佔空比 0 (靜止)
    pwm_a.start(0)
    pwm_b.start(0)
    print("GPIO Setup Complete. PWM Started.")

def set_motor_left(speed):
    """
    設定左馬達 (Motor A) 的速度與方向
    speed: 範圍 -100 ~ 100 
           正值為正轉 (前進)，負值為反轉 (後退)，0 為停止
    """
    if speed > 0:
        # 正轉
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        pwm_a.ChangeDutyCycle(speed)
    elif speed < 0:
        # 反轉
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        pwm_a.ChangeDutyCycle(-speed) # 取絕對值做為佔空比
    else:
        # 停止 (煞車)
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        pwm_a.ChangeDutyCycle(0)

def set_motor_right(speed):
    """
    設定右馬達 (Motor B) 的速度與方向
    speed: 範圍 -100 ~ 100 
    """
    if speed > 0:
        # 正轉 (注意：若馬達接反，這裡可能要改成 HIGH/LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
        pwm_b.ChangeDutyCycle(speed)
    elif speed < 0:
        # 反轉
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
        pwm_b.ChangeDutyCycle(-speed)
    else:
        # 停止
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        pwm_b.ChangeDutyCycle(0)

def move_forward(speed=50):
    print(f"Moving Forward (Speed: {speed})")
    set_motor_left(speed)
    set_motor_right(speed)

def move_backward(speed=50):
    print(f"Moving Backward (Speed: {speed})")
    set_motor_left(-speed)
    set_motor_right(-speed)

def turn_left(speed=40):
    # 原地左轉：左輪後退，右輪前進
    print(f"Turn Left (Speed: {speed})")
    set_motor_left(-speed)
    set_motor_right(speed)

def turn_right(speed=40):
    # 原地右轉：左輪前進，右輪後退
    print(f"Turn Right (Speed: {speed})")
    set_motor_left(speed)
    set_motor_right(-speed)

def stop():
    print("Stop")
    set_motor_left(0)
    set_motor_right(0)

def main():
    try:
        setup()
        
        # --- 測試流程 ---
        
        # 1. 前進 2 秒 (50% 速度)
        move_forward(50)
        time.sleep(2)
        stop()
        time.sleep(1)

        # 2. 後退 2 秒 (50% 速度)
        move_backward(50)
        time.sleep(2)
        stop()
        time.sleep(1)

        # 3. 左轉 2 秒 (40% 速度)
        turn_left(40)
        time.sleep(2)
        stop()
        time.sleep(1)

        # 4. 右轉 2 秒 (40% 速度)
        turn_right(40)
        time.sleep(2)
        stop()
        time.sleep(1)

        # 5. 加速測試 (0 -> 100%)
        print("Accelerating...")
        for dc in range(0, 101, 5):
            set_motor_left(dc)
            set_motor_right(dc)
            time.sleep(0.1)
        
        time.sleep(1)
        
        # 6. 減速測試 (100% -> 0)
        print("Decelerating...")
        for dc in range(100, -1, -5):
            set_motor_left(dc)
            set_motor_right(dc)
            time.sleep(0.1)
            
        stop()

    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # 程式結束時務必停止 PWM 並清理 GPIO 狀態
        print("Cleaning up GPIO...")
        if 'pwm_a' in globals(): pwm_a.stop()
        if 'pwm_b' in globals(): pwm_b.stop()
        GPIO.cleanup()
        print("Done.")

if __name__ == '__main__':
    main()
