#! /usr/bin/python3
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib as RPI
import time
import sys
import csv
import json

path = "/home/pi/Desktop/translation_stage/"
class Stage:
    currPos = 0.00
    def __init__(self):
        try:
            fr = open(path+"pos.txt")
            self.currPos = float(fr.read().strip())
        finally:
            fr.close()

    def update(self, toMove):
        if self.currPos + toMove > 140 or self.currPos + toMove < 0:
            print("Error: attempting to move out of bounds")
            sys.exit(-1)
        else:
            self.currPos+=toMove
        try:
            fw=open(path+"pos.txt","w")
            fw.write(str(self.currPos))
            with open(path+"table.txt", "a") as csvfile:
                csvwriter=csv.writer(csvfile)
                csvwriter.writerow([self.currPos])
                csvfile.close()
        finally:
            fw.close()

try:
    position = float(sys.argv[1]) # new position in mm
    speed = 2 # time to move specified distance
except:
    print("Usage: ./move_to_position position")
    sys.exit(1)

theStage = Stage()
distance = position - theStage.currPos
theStage.update(distance)
print(str(theStage.currPos))
rotation = False
if distance < 0:
    rotation = True
else:
    rotation = False
steps = int((abs(distance)) * 199.6054)
GPIO.setmode(GPIO.BCM)
GPIO_pins = (5, 6, 13)
direction = 10
pul = 11
en = 9
total_time = speed
time_per_step = 0.00025
my_motor = RPI.A4988Nema(direction, pul, GPIO_pins, "DRV8825")
GPIO.setup(en, GPIO.OUT)
GPIO.output(en, True)
start = time.time()
my_motor.motor_go(rotation, "Half", steps, time_per_step, True, 0.05 )
end = time.time()
#print("Motor move time: %s seconds" % (end - start))
#x = input("Enter y to continue")
#start2 = time.time()
#my_motor.motor_go(not rotation, "Half", steps, time_per_rev, True, 0.05 )
#end2 = time.time()
#print("Motor move time: %s seconds" % (end2 - start2))
GPIO.output(en, False)
GPIO.cleanup()
