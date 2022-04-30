from tracemalloc import start
import wave
import os
from vimba import *
import subprocess
import numpy as np
from PIL import Image
import sys
import math

def run_camera_wavelength(resolution=5, start_wavelength=400, end_wavelength=700, obj_dist=-1, directory="../captured_images"):
    '''this function takes a start, end wavelength then takes images at every resolution and stores them in dir. The object distance
    parameter is also required to determine movement on the pi. 
    '''
    for pic in os.scandir(f'{directory}'):
        os.remove(pic.path)
    wavelength_range=end_wavelength-start_wavelength
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            num_images=math.ceil(wavelength_range/resolution)+1
            images_taken=0
            curr_wavelength=start_wavelength # starting wavelength
            # object_distance=1356 # inf
            done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", f"Desktop/translation_stage/move_wavelength.py {curr_wavelength} {obj_dist}"],stdout=subprocess.DEVNULL) # move to 400nm
            if(done.check_returncode()==None):
                for frame in cam.get_frame_generator(limit=num_images):
                    curr_wavelength = start_wavelength + images_taken*(wavelength_range/(num_images-1))
                    print(f"Image captured at {curr_wavelength} nm")
                    done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", f"Desktop/translation_stage/move_wavelength.py {curr_wavelength} {obj_dist}"],stdout=subprocess.DEVNULL)
                    if(done.check_returncode()==None):
                        image=np.reshape(frame.as_numpy_ndarray(),(frame.as_numpy_ndarray().shape[0],frame.as_numpy_ndarray().shape[1]))
                        im=Image.fromarray(image)
                        im.save(f'{directory}/slice_{int(curr_wavelength)}.png')
                        images_taken+=1
                    else:
                        print("Error communicating with translation stage")
                        sys.exit(0)

def run_camera_distance(num_images, d_to_start, d_to_end, directory):
    '''
    this function takes a start, end DISTANCES then takes num_images distributed along the distance range in dir. 
    '''
    #TODO finish function, figure out a good way to label images (possibly query pos.txt, that way we can easily move to best position when done)
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            images_taken=0
            dist_increments=(d_to_end-d_to_start)/num_images
            # object_distance=1356 # inf
            done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", f"Desktop/translation_stage/move_dist.py {d_to_start}"],stdout=subprocess.DEVNULL)
            p=subprocess.Popen(["ssh",  "pi@192.168.5.1", "cat", "Desktop/translation_stage/pos.txt"],stdout=subprocess.PIPE)
            curpos, err = p.communicate()
            curpos=curpos.decode("utf-8")
            if(done.check_returncode()==None):
                print(num_images)
                for frame in cam.get_frame_generator(limit=int(num_images)):
                    if(done.check_returncode()==None):
                        image=np.reshape(frame.as_numpy_ndarray(),(frame.as_numpy_ndarray().shape[0],frame.as_numpy_ndarray().shape[1]))
                        im=Image.fromarray(image)
                        im.save(f'{directory}/slice_{curpos}.png')
                        images_taken+=1
                    else:
                        print("Error communicating with translation stage")
                        sys.exit(0)
                    print(f"Image captured at {curpos}")
                    done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", f"Desktop/translation_stage/move_dist.py {dist_increments}"],stdout=subprocess.DEVNULL)
                    p=subprocess.Popen(["ssh",  "pi@192.168.5.1", "cat", "Desktop/translation_stage/pos.txt"],stdout=subprocess.PIPE)
                    curpos, err = p.communicate()
                    curpos=curpos.decode("utf-8")

def main():
    try:
        w1=float(sys.argv[1])
        w2=float(sys.argv[2])
        od=float(sys.argv[3])
        r=int(sys.argv[4])
        directory=sys.argv[5].strip()
        if r < 1:
            print("resolution must be at least 1nm")
    except:
        print('Usage: camera.py starting_wavelength(nm), ending_wavelength(nm), object_distance(mm), hypercube_resolution(nm), directory_location (string)')
        exit(0)
    run_camera_wavelength(r, w1, w2, od)

if __name__ == '__main__':
    main()