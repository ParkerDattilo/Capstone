def bfd_calculation(wavelength, obj_dist):
    '''
    This function calculates the bi-focal distance 
    based on the given wavelength and obj_distance
     and the constant parameters of our optical
    system. Input is assumed to be in nm for 
    wavelength and mm for distance
    '''
    wavelength*=10**-9
    obj_dist*=10**-3
    d2=-0.00654
    flens=0.12551
    f0=0.572
    lam0=555*10**-9
    if obj_dist <= 0: #object at infinity
        dist_recip=0
    else:
        dist_recip=-1/obj_dist
    return 1000*(1/(dist_recip + (1/flens))+(d2-(wavelength*flens**2)/(lam0*f0)))