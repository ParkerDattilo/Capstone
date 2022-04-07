#! /usr/bin/python3
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib as RPI

direction = 21
pul = 26
en = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(direction, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.setup(pul, GPIO.OUT)
GPIO.output(en, False)
GPIO.output(direction, False)
GPIO.output(pul, False)
GPIO.cleanup()
