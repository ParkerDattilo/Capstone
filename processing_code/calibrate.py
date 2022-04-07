from camera import run_camera_distance, run_camera_distance
from bfd import bfd_calculation
import math
import mahotas as mh
import os
import sys
from skimage import io
from intensity_plot import focus_measure
import numpy as np
import subprocess

def calibrate_focus(known_wavelength, known_obj_distance, resolution=5, w_range=100):
    '''
    This function assumes that the detector is already in a position that is a "pretty good" estimate of best focus for the given wavelength
    The known_* inputs are passed to the pi in order to set the calibration to the known wavelength after determining the true best focus image
    near the given wavelength. The other parameters determine the degree of calibration that the user is interested in, w_range is the
    full wavelength sweep it performs around the known wavelength (+/- w_range/2) and resolution determines the increments at which to
    take images. Total number of images is w_range/resolution +1, so the larger this ratio the longer calibration will take. Make sure
    the calibration Images folder is empty!!!
    '''
    # maybe figure out a way to clear these images afterwards?
    # done=subprocess.run(["del",  "/s", "/q", "C:\\Users\\parke\\OneDrive\\Documents\\Desktop\\Spring 2022\\Capstone\\im_proc\\calibration_images\\"],stdout=subprocess.DEVNULL)
    for pic in os.scandir('../calibration_images'):
        os.remove(pic.path)
    w_start = known_wavelength - w_range/2
    w_end = known_wavelength + w_range/2
    # because we are calibrating the wavelength offset value, we need to be working with solely stage relative values. the position returned from
    # the bfd will not be correct since that position has an unknown offset, however the difference between 2 positions does not depend on that
    # offset, so we will use the move_dist function to know where to start taking images
    w_start_pos=bfd_calculation(w_start,known_obj_distance)
    w_guess_pos=bfd_calculation(known_wavelength,known_obj_distance)
    w_end_pos=bfd_calculation(w_end,known_obj_distance)
    print(w_start,w_end)
    print(known_obj_distance)
    print(w_start_pos,w_guess_pos,w_end_pos)

    #sign shouldn't matter, just determines which direction it moves in first
    d_to_start = w_guess_pos-w_start_pos
    print(d_to_start)
    d_to_end = w_guess_pos-w_end_pos 
    print(d_to_end)
    num_images=(w_range/resolution)+1
    run_camera_distance(num_images, d_to_start, d_to_end, "../calibration_images")
    #now that all the calibration images are taken, we need to select the most in focus one, then move to the pi to that position
    #since the image is supposed to be taken over a small region, we can likely just use the focus measure of the whole image
    FM = 0
    for pic in os.scandir('../calibration_images'):
        image = io.imread(pic.path)
        # print(image)
        image=image-np.amin(image)
        image = image/np.amax(image)
        curFocus = focus_measure(image)
        if curFocus > FM:
            FM = curFocus
            bestImage = pic.path
    # now, bestImage is the path to the correct image. We can read the path for the position value and move to that position
    print(bestImage.split("_"))
    position = float(bestImage.split('_')[2].split(".png")[0])
    print(f"Best position at {position}, moving there now...")
    #finally, move to that position and call the calibration script on the pi
    done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", f"Desktop/translation_stage/move_to_pos.py {position}"],stdout=subprocess.DEVNULL)
    done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", "Desktop/translation_stage/calibrate_wavelength.py", str(known_wavelength), str(known_obj_distance)],stdout=subprocess.DEVNULL)

def main():
    try:
        wl=float(sys.argv[1])
        od=float(sys.argv[2])
        r=int(sys.argv[3])
        w_range=float(sys.argv[4])
    except:
        print("Usage: python3 calibrate.py known_wavelength(nm) object_distance (mm) resolution (nm) wavelength_range (nm)")
        sys.exit(0)
    calibrate_focus(wl, od, r, w_range)

if __name__ == "__main__":
    main()

