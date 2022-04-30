from matplotlib.pyplot import imread, plot, savefig
import numpy as np
import mahotas as mh
import matplotlib.pyplot as plt
from skimage import io
import os

def focus_measure(im_to_convolove):
    Sx = np.array([[1,2,1],[0,0,0],[-1,-2,-1]])
    Gx = mh.convolve(im_to_convolove, Sx)
    Gy = mh.convolve(im_to_convolove, Sx.transpose())
    G = np.square(Gx) + np.square(Gy)
    return np.square(np.std(G))

def focus_plot(tl_coord, br_coord, plot_num):
    # p1 = input("Enter the first set of x-y coordinates (top left corner of desired region): ")
    # *6 is because displayed coordinates are downscaled from captured image coordinates by factor of 6
    x1=tl_coord[0]*6
    y1=tl_coord[1]*6
    # p2 = input("Enter the second set of x-y coordinates (bottom right corner of desired region): ")
    x2=br_coord[0]*6
    y2=br_coord[1]*6

    FM=[]
    first_im=-1
    second_im=-1
    for pic in os.scandir('../captured_images'):
        if second_im < 0 and first_im > 0:
            second_im=float(pic.path.split('slice_')[1].split('.')[0])
            print(f"second: {second_im}")
        if first_im < 0:
            first_im=float(pic.path.split('slice_')[1].split('.')[0])
            print(f"first: {first_im}")
        image = io.imread(pic.path)
        # print(image)
        image=image-np.amin(image)
        image = image/np.amax(image)

        # image = mh.colors.rgb2gray(image[:,:,0:3])
        im_crop = image[int(y1):int(y2),int(x1):int(x2)]


        # Gx = mh.convolve(im_crop, Sx)
        # Gy = mh.convolve(im_crop, Sx.transpose())
        # G = np.square(Gx) + np.square(Gy)
        FM.append(focus_measure(im_crop))
    FM = FM - np.amin(FM)
    FM = FM/np.amax(FM)
    x_axis = []
    val=first_im
    res=second_im-first_im
    for i in range(0,len(FM)):
        x_axis.append(val)
        val+=res
    print(x_axis[np.argmax(FM)])
    im=imread('./combined_image.png')
    f, (ax1,ax2)=plt.subplots(1,2,figsize=(6,2.3))
    ax1.imshow(im[int(y1):int(y2),int(x1):int(x2)])
    ax2.plot(x_axis,FM, 'r-')
    ax2.set_xlabel("Wavelength (nm)")
    ax2.set_ylabel("Normalized TENV Measure")
    plt.savefig(f'../selected_plot_{plot_num}.png')
    # plt.show()
# if __name__ == "__main__":
#     main()
# r = io.imread("red_real.png")
# r = mh.colors.rgb2gray(r[:,:,0:3])
# g = io.imread("green_real.png")
# g = mh.colors.rgb2gray(g[:,:,0:3])
# b = io.imread("blue_real.png")
# b = mh.colors.rgb2gray(b[:,:,0:3])
# p1 = input("Enter the first set of x-y coordinates (top left corner of desired region): ")
# x1,y1=p1.split(' ')
# p2 = input("Enter the second set of x-y coordinates (bottom right corner of desired region): ")
# x2,y2=p2.split(' ')
# gray()
# plt.figure()
# f, axarr = plt.subplots(3,1)
# rc = r[int(y1):int(y2),int(x1):int(x2)]
# gc = g[int(y1):int(y2),int(x1):int(x2)]
# bc = b[int(y1):int(y2),int(x1):int(x2)]
# axarr[0].imshow((r[int(y1):int(y2),int(x1):int(x2)]))
# axarr[0].set_title("red_wavelength")
# axarr[1].imshow((g[int(y1):int(y2),int(x1):int(x2)]))
# axarr[1].set_title("green_wavelength")
# axarr[2].imshow((b[int(y1):int(y2),int(x1):int(x2)]))
# axarr[2].set_title("blue_wavelength")
# BREN FM
# [M, N] = rc.shape
# DH = np.zeros((M, N));
# DV = np.zeros((M, N));
# DV[1:M-2,:] = rc[3:,:]-rc[1:-2,:]
# DH[:,1:N-2] = rc[:,3:]-rc[:,1:-2]
# FM_R = np.maximum(DH, DV);        
# FM_R = np.square(FM_R)
# FM_R = np.mean(FM_R);

# Sx = np.array([[1,2,1],[0,0,0],[-1,-2,-1]])

# Gx = mh.convolve(rc, Sx)
# Gy = mh.convolve(rc, Sx.transpose())
# G = np.square(Gx) + np.square(Gy)
# FM_R = np.square(np.std(G))

# [M, N] = gc.shape
# DH = np.zeros((M, N));
# DV = np.zeros((M, N));
# DV[1:M-2,:] = gc[3:,:]-gc[1:-2,:]
# DH[:,1:N-2] = gc[:,3:]-gc[:,1:-2]
# FM_G = np.maximum(DH, DV);        
# FM_G = np.square(FM_G)
# FM_G = np.mean(FM_G);

# Gx = mh.convolve(gc, Sx)
# Gy = mh.convolve(gc, Sx.transpose())
# G = np.square(Gx) + np.square(Gy)
# FM_G = np.square(np.std(G))

# [M, N] = bc.shape
# DH = np.zeros((M, N));
# DV = np.zeros((M, N));
# DV[1:M-2,:] = bc[3:,:]-bc[1:-2,:]
# DH[:,1:N-2] = bc[:,3:]-bc[:,1:-2]
# FM_B = np.maximum(DH, DV);        
# FM_B = np.square(FM_B)
# FM_B = np.mean(FM_B);

# Gx = mh.convolve(bc, Sx)
# Gy = mh.convolve(bc, Sx.transpose())
# G = np.square(Gx) + np.square(Gy)
# FM_B = np.square(np.std(G))

# print("Red average intensity: ")
# print(np.mean(r[int(y1):int(y2),int(x1):int(x2)]))
# print("Red focus (Bren): ")
# print(FM_R)
# print("-----------------------")
# print("Green average intensity: ")
# print(np.mean(g[int(y1):int(y2),int(x1):int(x2)]))
# print("Green focus (Bren): ")
# print(FM_G)
# print("-----------------------")
# print("Blue average intensity: ")
# print(np.mean(b[int(y1):int(y2),int(x1):int(x2)]))
# print("Blue focus (Bren): ")
# print(FM_B)

# plt.show()

