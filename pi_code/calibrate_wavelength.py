#!/usr/bin/python3
import sys
import os

def calibrate_w_offset(known_wavelength, obj_dist):
# this function will calibrate the current position based on a known wavelength at a known distance. This calibration adjusts the current position to be relative to the back lens of the system, since that is where the calculated value assumes the measurement is taken from
# It is assumed that the translation stage is already in a position where the wavelength
# input is in focus in the image. The wavelength-to-position formula will calculate expected
# position from the focus lens, and the difference between that and the current position will determine
# the offset. The outputs of this function will output the offset to offset.txt where it can be read by the wavelength function
#NOTE do NOT update the curpos, that will screw up all other movements. This offset is solely for the purpose of wavelength calculation.

    path="/home/pi/Desktop/translation_stage/"
    object_dist*=10**-3 #input in mm
    known_wavelength=known_wavelength*10**-9 #input in nm
    fpos = open(path+"pos.txt", "r")
    curpos = float(fpos.read().strip())
    d2=-0.00654
    flens=0.12551
    f0=0.572
    lam0=555*10**-9
    if obj_dist <=0:
        dist_recip=0
    else:
        dist_recip=-1/obj_dist
    dist_from_lens=1/(dist_recip+(1/flens))+(d2-(known_wavelength*flens**2)/(lam0*f0))
    dist_from_lens*=1000
    offset = dist_from_lens - curpos
    fo=open(path+"offset.txt", "w")
    fo.write(str(offset))


def main():
    try:
        input_lambda=float(sys.argv[1])
        obj_dist=float(sys.argv[2])
    except:
        print("Usage: ./calbrate_wavelength.py input_wavelength(nm) object_distance(mm)")
        sys.exit(0)
    calibrate_w_offset(input_lambda, obj_dist)
main()
