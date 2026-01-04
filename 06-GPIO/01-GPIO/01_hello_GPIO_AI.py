import Jetson.GPIO as GPIO
print(GPIO.VERSION)
print(GPIO.RPI_INFO)
print("123")

# 幫我寫一個9x9乘法
def multiplication_table():
    for i in range(1, 10):
        for j in range(1, 10):
            print(f"{i} x {j} = {i*j}", end="\t")
        print()

multiplication_table()


# 把gpio 18閃爍  每秒1次
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

try:
    while True:
        GPIO.output(18, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)