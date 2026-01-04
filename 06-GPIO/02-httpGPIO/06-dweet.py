import RPi.GPIO as GPIO
import time
import requests

# 設定為物理引脚編號模式
GPIO.setmode(GPIO.BOARD)

# 定義物理引脚11（對應BCM GPIO 17）
BUTTON_PIN = 11

# 設置該引脚為輸入模式，且使用內置上拉電阻
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# dweet.io的URL和您的"thing"名稱
DWEET_URL = "https://dweet.io/dweet/for/"
THING_NAME = "your-unique-thing-name"  # 請替換為您自己的thing名稱

def send_dweet(button_state):
    try:
        # 根據按鈕是否被按下來設定狀態
        state = '1' if button_state == GPIO.LOW else '0'
        # 發送HTTP請求到dweet.io
        r = requests.get(f"{DWEET_URL}{THING_NAME}?button={state}")
        # 檢查請求是否成功
        if r.status_code == 200:
            print(f"按鈕狀態 {state} 已發送到dweet.io")
        else:
            print(f"發送失敗，狀態碼：{r.status_code}")
    except Exception as e:
        print(f"發送請求時出錯：{e}")

try:
    while True:
        # 讀取按鈕狀態
        button_state = GPIO.input(BUTTON_PIN)

        # 發送按鈕狀態到dweet.io
        send_dweet(button_state)

        # 等待0.5秒，降低CPU負擔
        time.sleep(2)

except KeyboardInterrupt:
    # 如果按下Ctrl+C，清除GPIO配置並退出程式
    GPIO.cleanup()
