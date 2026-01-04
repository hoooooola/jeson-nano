
import Jetson.GPIO as GPIO
import time
 
def main():
    prev_value = None

    # Pin Setup:
    GPIO.setmode(GPIO.BOARD )   
    GPIO.setup(7, GPIO.IN)  # set pin as an input pin
    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            value = GPIO.input(7)            
            print("Value read from pin {} : {}".format(7,value)) 
            time.sleep(1)
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()


'''
123
'''
