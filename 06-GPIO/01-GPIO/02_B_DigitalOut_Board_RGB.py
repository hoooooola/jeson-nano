
import RPi.GPIO as GPIO
import time

# Pin Definitions 

def main():
    # Pin Setup:
    GPIO.setmode(GPIO.BOARD)  # BCM pin-numbering scheme from Raspberry Pi
    # set pin as an output pin with optional initial state of HIGH
    GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) # B
    GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW) # G
    GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW) # R

    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            GPIO.output(12, 1)        
            time.sleep(2)
            GPIO.output(12, 0) 
            GPIO.output(16, 1)        
            time.sleep(2)
            GPIO.output(16, 0) 
            GPIO.output(18, 1)        
            time.sleep(2)
            GPIO.output(18, 0)                          
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
