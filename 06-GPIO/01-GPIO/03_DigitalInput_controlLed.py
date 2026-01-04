import Jetson.GPIO as GPIO
import time
 
def main():
    prev_value = None

    # Pin Setup:
    GPIO.setmode(GPIO.BOARD )   
    GPIO.setup(7, GPIO.IN)  # set pin as an input pin
    GPIO.setup(12, GPIO.OUT)  # set pin as an output pin
    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            value = GPIO.input(7)            
            print("Value read from pin {} : {}".format(7,value)) 
            if value == 1:
                GPIO.output(12, GPIO.HIGH)
            else:
                GPIO.output(12, GPIO.LOW)
            time.sleep(1)
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()


'''
import Jetson.GPIO as GPIO
import time
 
def main():
    prev_value = None

    # Pin Setup:
    GPIO.setmode(GPIO.BOARD )   
    GPIO.setup(7, GPIO.IN)  # set pin as an input pin
    GPIO.setup(12, GPIO.OUT)  # set pin as an output pin
    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            value = GPIO.input(7)            
            print("Value read from pin {} : {}".format(7,value)) 
            GPIO.output(12, GPIO.value)
            time.sleep(1)
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
'''
