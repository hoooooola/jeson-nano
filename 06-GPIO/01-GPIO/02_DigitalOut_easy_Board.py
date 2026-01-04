import Jetson.GPIO as GPIO                                 # 匯入GPIO
import time                                             #  匯入 時間
 
  
#GPIO.setmode(GPIO.BCM)        # BCM pin-numbering scheme from Raspberry Pi
GPIO.setmode(GPIO.BOARD)     # Board pin-numbering scheme from Raspberry Pi
GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH)        # 設定GPIO18輸出高電位 

print("Starting demo now! Press CTRL+C to exit")      # 列印
curr_value = 1                # 變數 curr_value  高電位
try:
    while True:                                                                  # 無限迴圈
            time.sleep(1)                                                       # 休息1秒  
            print("Outputting {} to pin {}".format(curr_value, 12))  # 列印
            GPIO.output(12, curr_value)                # 改變接腳的電位
            curr_value ^= GPIO.HIGH                    #   相反
finally:
        GPIO.cleanup()                                                      # 回復GPIO 
