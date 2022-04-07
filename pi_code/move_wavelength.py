#!/usr/bin/python3
import sys
import subprocess

path="/home/pi/Desktop/translation_stage/"

try:
    wavelength=float(sys.argv[1])
    wavelength=wavelength*10**-9 #input in nm
    object_dist=float(sys.argv[2])
    object_dist*=10**-3 #input in mm
except:
    print("Usage: ./move_wavelength.py wavelength(nm) object_distance(mm)")
    sys.exit(0)
f = open(path+"offset.txt")
offset = float(f.read())
f.close()
d2=-0.00654
flens=0.12551
f0=0.572
lam0=555*10**-9
if object_dist <= 0: #object at infinity
    dist_recip=0
else:
    dist_recip=-1/object_dist 
bfd=1/(dist_recip + (1/flens))+(d2-(wavelength*flens**2)/(lam0*f0))
bfd=bfd*1000 - offset
bash="python3 "+path+"move_to_pos.py "+str(bfd)
print(str(bfd))
process=subprocess.Popen(bash.split(), stdout=subprocess.DEVNULL)
output, error=process.communicate()
