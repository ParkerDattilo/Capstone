from matplotlib.pyplot import gray, imread, imsave
import mahotas as mh
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from pylab import imshow, show, figure, title
import os
import time

def wavelength_to_rgb(wavelength, gamma=0.8):

    '''This converts a given wavelength of light to an 
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    '''

    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return [int(R), int(G), int(B)]

start = time.perf_counter()
cube = []
for pic in os.scandir('./captured_images'):
    im = imread(pic.path)
    cube.append(im)

# redIm = imread("red_real.png")
# r = mh.colors.rgb2gray(redIm[:,:,0:3])
# blueIm = imread("blue_real.png")
# b = mh.colors.rgb2gray(blueIm[:,:,0:3])
# greenIm = imread("green_real.png")
# g = mh.colors.rgb2gray(greenIm[:,:,0:3])


# image = np.array([r[:518,:620],g[:518,:620],b[:518,:620]])

stack,h,w = np.shape(cube)
# stack,h,w = image.shape
focus = np.array([mh.sobel(t, just_filter=True) for t in cube])
# focus = np.array([mh.sobel(t, just_filter=True) for t in image])
best = np.argmax(focus, 0)
# conv_width=40
# conv_height=40
# conv_filter=np.ones((conv_width,conv_height),bool)
gray()

# r_sob = mh.sobel(r[:518,:620], just_filter=True)
# v_r = mh.convolve(r_sob, conv_filter)
# r_mask=np.where(v_r==v_r.max())
# imshow(r_sob)
# title("R")
# show()

# g_sob = mh.sobel(g[:518,:620], just_filter=True)
# v_g = mh.convolve(g_sob, conv_filter)
# g_mask=np.where(v_g==v_g.max())
# imshow(g_sob)
# title("G")
# show()

# b_sob = mh.sobel(b[:518,:620], just_filter=True)
# v_b = mh.convolve(b_sob, conv_filter)
# b_mask=np.where(v_b==v_b.max())
# imshow(b_sob)
# title("B")
# show()


imshow(best)
title("Best")
show()

color_map=[]
wl=400
for k in range(0,61):
    color_map.append(wl)
    wl+=5  

rgb = np.zeros((2056, 2464, 3))
for i in range(0,2056):
    for j in range(0,2464):
        curr_wl=color_map[best[i,j]]
        if curr_wl>=650:
            rgb[i,j,:] = [0,0,0]
        else:
            rgb[i,j,:] = wavelength_to_rgb(curr_wl)
        # if best[i,j] == 0:
        #     # red
        #     rgb[i,j,:] = wavelength_to_rgb(650)
        # elif best[i,j] == 1:
        #     # green
        #     rgb[i,j,:] = wavelength_to_rgb(550)
        # elif best [i,j] == 2:
        #     # blue
        #     rgb[i,j,:] = wavelength_to_rgb(450)

imshow(rgb)
title("RGB")
show()

image = np.array(cube)
image = image.reshape((stack, -1))
image = image.transpose()
r = image[np.arange(len(image)), best.ravel()]
r = r.reshape((h,w))
fig, ax = plt.subplots()

# rec_r = patches.Rectangle((r_mask[1][0]-conv_width,r_mask[0][0]-conv_height), 2*conv_width, 2*conv_height, linewidth=3, edgecolor='r', facecolor='none', ls='--')
# rec_g = patches.Rectangle((g_mask[1][0]-conv_width,g_mask[0][0]-conv_height), 2*conv_width, 2*conv_height, linewidth=3, edgecolor='g', facecolor='none', ls='-')
# rec_b = patches.Rectangle((b_mask[1][0]-conv_width,b_mask[0][0]-conv_height), 2*conv_width, 2*conv_height, linewidth=3, edgecolor='b', facecolor='none', ls='-.')
# ax.add_patch(rec_r)
# ax.add_patch(rec_g)
# ax.add_patch(rec_b)

gray()
ax.imshow(r)
end = time.perf_counter()
print(f"Done in {start-end:0.3f} seconds")
imsave('combined_image.png',r)
plt.title("Combined Image")
plt.savefig("processed_image.png")
plt.show()

