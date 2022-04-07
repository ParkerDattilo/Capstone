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
pul_per_rev= 1000
total_time = 8
time_per_rev = total_time/(num_revs * pul_per_rev)
my_motor = RPI.A4988Nema(direction, pul, GPIO_pins, "DRV8825")
GPIO.setup(en, GPIO.OUT)
GPIO.output(en, True)
start = time.time()
my_motor.motor_go(False, "Half", pul_per_rev*num_revs, time_per_rev, True, 0.05 )
end = time.time()
print("Motor move time: %s seconds" % (end - start))
x = input("Enter y to continue")
start2 = time.time()
my_motor.motor_go(True, "Half", pul_per_rev*num_revs, time_per_rev, True, 0.05 )
end2 = time.time()
print("Motor move time: %s seconds" % (end2 - start2))
GPIO.output(en, False)
GPIO.cleanup()
