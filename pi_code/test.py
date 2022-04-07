#! /usr/bin/python3
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib as RPI
import time

GPIO.setmode(GPIO.BCM)
GPIO_pins = (5, 6, 13)
direction = 21
pul = 26
en = 19
num_revs = 10
pul_per_rev= 400
time_to_move = 2
time_per_step = time_to_move/(num_revs * pul_per_rev * 2)
my_motor = RPI.A4988Nema(direction, pul, GPIO_pins, "DRV8825")
GPIO.setup(en, GPIO.OUT)
GPIO.output(en, True)
start = time.time()
my_motor.motor_go(False, "Half", pul_per_rev*num_revs, time_per_step, True, 0.05 )
print("Motor move time: %s seconds" % (time.time()-start))
my_motor.motor_go(True, "Half", pul_per_rev*num_revs, time_per_step, True, 0.05 )
GPIO.output(en, False)
GPIO.cleanup()
