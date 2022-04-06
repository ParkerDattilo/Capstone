def bfd_calculation(wavelength, obj_dist):
    '''
    This function calculates the bi-focal distance based on the given wavelength and obj_distance and the constant parameters of our optical
    system
    '''
    d2=0.00654
    flens=0.12551
    f0=0.572
    lam0=55*10**-9
    if obj_dist <= 0: #object at infinity
        dist_recip=0
    else:
        dist_recip=-1/obj_dist
    return 1/(dist_recip + (1/flens))+(d2-(wavelength*flens**2)/(lam0*f0))