SERVO2 = 18
import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO2, GPIO.OUT)

def setServoAngle(servo, angle):
    pwm = GPIO.PWM(servo, 50)
    pwm.start(8)
    dutyCycle = angle / 18. +3.
    pwm.ChangeDutyCycle(dutyCycle)
    time.sleep(0.1)
    pwm.stop()

setServoAngle(SERVO2,0)