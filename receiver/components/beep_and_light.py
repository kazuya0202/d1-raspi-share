import RPi.GPIO as GPIO
import time


if __name__ == "__main__":
    pin = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(15, GPIO.OUT)
    p = GPIO.PWM(pin, 1)

    p.start(50)
    p.ChangeFrequency(261)
    GPIO.output(15, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(15, GPIO.LOW)

    p.stop()
    GPIO.cleanup()
