import sys
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import skimage as skimg
import scipy.ndimage as ndi


#TODO: implement a radon transform version of this for batch processing on GPU
def vectorize_streamlines(x, y, u, v, start, density = 80, maxlength=0.5):
    '''
    generates a vector streamline beginning at start and propagating in the direction indicated by vector field.
    x = x location of vector, as generated by meshgrid
    y = y location of vector
    u = x components
    v = y components
    start = tuple representing seed point
    density = sampling factor, with 1 = 30 samples across image
    '''
    
    seed_pt = np.array([[start[0]], [start[1]]])
    sl = plt.streamplot(x, y, u, v, 
        density=density, 
        broken_streamlines=False, 
        start_points=seed_pt.T,
        integration_direction='forward',
        maxlength=maxlength
        )

    lineseg = sl.lines.get_segments()

    #round to 1 decimal place and remove duplicates
    verts = np.array([lineseg[i][0] for i in range(len(lineseg))])
    #verts = [[int(np.rint(vert[0])),int(np.rint(vert[1]))] for vert in verts]
    rounding_precision = 1
    verts = np.around(verts, rounding_precision)
    
    verts, idx = np.unique(verts, axis = 0, return_index=True)
    
    verts = verts[np.argsort(idx)]
    
    plt.gca().remove()

    return verts

def create_stream_pair(x, y, u, v, ub, vb, start, end, density = 80, maxlength=0.5, origin = (0,0)):
    '''
    takes two vector fields and two points and creates streamline pairs propagating in opposite directions
    x = x location of vectors
    y = y location of vectors
    u = x component of field 1
    v = y component of field 1
    ub = x component of field 2 ('backwards' field)
    vb = y component of field 2
    start = seed point in field 1
    end = seed point in field 2
    density = sampling factor
    ''' 

    # deal with issue where if angle goes in an odd way, streamplot doesn't like it.
    start_angle     = np.arctan2(start[1]-origin[1], start[0]-origin[0])
    # start_angle    += 2*np.pi*(start_angle<0)
    end_angle       = np.arctan2(end[1]-origin[1], end[0]-origin[0])
    
    swap_pts = ((end_angle-start_angle < 0)*(start_angle-end_angle<np.pi)) or (end_angle-start_angle>np.pi)

##    print("start: "+str(start))
##    print("end: "+str(end))
##
##    print("start_angle: "+str(start_angle))
##    print("end_angle: "+str(end_angle))
    if swap_pts:
        start, end = end, start


    sl1 = vectorize_streamlines(x, y, u, v, start, density, maxlength)
    sl2 = vectorize_streamlines(x, y, ub, vb, end, density, maxlength)

    return sl1, sl2


def apply_motion_blur(image, size, angle):
    #directional motion blur. returns image with [size] pixel motion blur in direction [angle] degrees.
    k = np.zeros((size, size), dtype=np.float32)
    k[ (size-1)// 2 , :] = np.ones(size, dtype=np.float32)
    k = cv2.warpAffine(k, cv2.getRotationMatrix2D( (size / 2 -0.5 , size / 2 -0.5 ) , angle, 1.0), (size, size) )  
    k = k * ( 1.0 / np.sum(k) )        
    return cv2.filter2D(image, cv2.CV_32F, k) 

def running_mean_uniform_filter1d(x, N):
    # moving average filter of length N, where the signal is wrapped (circular)
    return ndi.uniform_filter1d(x, N, mode='wrap', origin=-(N//2))[:-(N-1)]

def create_vec_field(
    img, 
    stride = 3, 
    win = 100, 
    tex_thresh = 40000, 
    pap_thresh = 30000, 
    origin = (3758, 3531), #TODO: make this selectable
    sub_angles = 6,
    alpha_v = 7e-5,
    sigma_v = 2.0,
    alpha_p = 5.0,
    beta_p = 2.0,
    gamma_p = 0.3,
    delta_p = 1.4,
    sigma = 3.0
    ):
    '''
    generates a vector field to trace papyrus layers based on textural and contextual information in img

    stride = downsampling factor (higher runs faster but is less accurate)
    win = window size for regions around query pixels (higher is slower but less noisy and less accurate)
    tex_thresh = threshold above which textures are to be ignored
    pap_thresh = threshold between papyrus and void
    origin = rotational center of layer, as tuple
    sub_angles = number of angular subdivisions for directional blur
    alpha_v = scaling factor for avoiding void when tracing
    sigma_v = region of influence for void avoidance effect
    alpha_p = region of influence for boundary tracing effect
    beta_p = region of zero influence for boundary tracing effect
    gamma_p = scaling factor for boundary tracing effect
    delta_p = whether boundary tracing force is attractive or repulsive, 1 is neutral
    sigma = size of smoothing kernel for resultant vector field
    '''

    N_y = img.shape[0]//stride + (-win)//stride
    N_x = img.shape[1]//stride + (-win)//stride

    dirs = np.zeros((N_y, N_x))

    #clip image at tex_thresh to enhance textures and remove high intensity noise
    clip_img = np.minimum(img, tex_thresh*np.ones(img.shape))
    hann = skimg.filters.window('hann', (win+1, win+1))
    for row in range(N_y):
        print('processing row {row} of {N_y}...'.format(row = row + 1, N_y = N_y))
        for col in range(N_x):
            scout = img[stride*row + win//2 - stride//2 : stride*row + win//2 + stride//2 + 1, stride*col + win//2 - stride//2 : stride*col + win//2 + stride//2 + 1]
            if np.mean(scout) > 0:
                #generate region of interest and analyse in frequency domain
                roi = clip_img[stride*row : stride*row + win+1, stride*col : stride*col + win+1]
                #roi = clip_img[stride*(row+1) : stride*(row+1) + win + 1, stride*(col+1) : stride*(col+1) + win+1]
                roi = roi * hann
                
                ft = np.abs(np.fft.fftshift(np.fft.fft2(roi)))
                
                r_max = 0.5*ft.shape[0]

                ftp = skimg.transform.warp_polar(ft, radius=r_max, output_shape=(180,20), center = (win/2, win/2))
                
                #identify dominant texture angle
                ang = np.sum(ftp, 1)
                ang = ang[0:90] + ang[90:180]
                #ang = moving_average(ang, 11) 
                ang = running_mean_uniform_filter1d(ang, 5)
                ang_max = np.argmax(ang);
                dirs[row, col] = 2*ang_max;

    print("done.")
    #upsample and pad to match original image size
    dirs = dirs.repeat(stride, 0).repeat(stride, 1)
    dirs = np.pad(dirs,(win//2, win//2))
    dirs = np.pad(dirs,((0, img.shape[0]-dirs.shape[0]),(0, img.shape[1]-dirs.shape[1])))

    #generate meshgrid for vector coordinates
    mesh = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    mesh = np.flip(mesh, 0) #permute axes to return x coordinate first

    #threshold image to distinguish between papyrus and void
    bin_img = img > pap_thresh
    bin_img = bin_img.astype(int)
    filled_img = np.zeros(bin_img.shape)
    filled_img = filled_img + np.multiply( 
            apply_motion_blur(bin_img, 10, 90), 
            (dirs < (90/sub_angles)) + (dirs >= (180-90/sub_angles))
            )

    #directional motion blur to fill small tears and holes
    for i in range(1, sub_angles):
        #probably not necessary to use multiply over *, but unsure how opencv overloads *
        filled_img = filled_img + np.multiply( 
            apply_motion_blur(bin_img, 10, 90 - i*180/sub_angles), 
            (dirs < (i*180/sub_angles + 90/sub_angles)) * (dirs >= (i*180/sub_angles - 90/sub_angles))
            )
    
    # generate circumferential unit vectors for orienting vectors ctr-clockwise (wrt graphing axes)
    ccwx = np.cos(np.pi/2 + np.arctan2(mesh[1]-origin[1], mesh[0]-origin[0]))
    ccwy = np.sin(np.pi/2 + np.arctan2(mesh[1]-origin[1], mesh[0]-origin[0]))
    u = -np.sin(np.radians(dirs)) #find normal to strongest texture
    v = np.cos(np.radians(dirs))

    # flip vectors as necessary to maintain ctr-clockwise rotation
    misoriented = u*ccwx + v*ccwy < 0
    u = u - 2*u*misoriented
    v = v - 2*v*misoriented
    
    filled_img = filled_img > 0.5
    filled_img = filled_img.astype(np.float32)

    u = u*filled_img 
    v = v*filled_img

    #Sobel operator on image, used in void
    dx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    dy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
    
    dxb = cv2.Sobel(filled_img, cv2.CV_32F, 1, 0)
    dyb = cv2.Sobel(filled_img, cv2.CV_32F, 0, 1)   #used in pap

    dx = alpha_v*skimg.filters.gaussian(dx, sigma = sigma_v, truncate =2.0)
    dx = dx*(1- filled_img)

    dy = alpha_v*skimg.filters.gaussian(dy, sigma = sigma_v, truncate =2.0)
    dy = dy*(1- filled_img)

    dxb = delta_p*alpha_p/beta_p*skimg.filters.gaussian(dxb, sigma=alpha_p, truncate =2.0) - skimg.filters.gaussian(dxb, sigma=beta_p, truncate =2.0)
    dxb = gamma_p*dxb*filled_img
    dyb = delta_p*alpha_p/beta_p*skimg.filters.gaussian(dyb, sigma=alpha_p, truncate =2.0) - skimg.filters.gaussian(dyb, sigma=beta_p, truncate =2.0)
    dyb = gamma_p*dyb*filled_img

    u = u + dx - dxb
    u = skimg.filters.gaussian(u, sigma = sigma, truncate =2.0)
    v = v + dy - dyb
    v = skimg.filters.gaussian(v, sigma = sigma, truncate =2.0)
    ub = -u + dx - dxb
    ub = skimg.filters.gaussian(ub, sigma = sigma, truncate =2.0)
    vb = -v + dy - dyb
    vb = skimg.filters.gaussian(vb, sigma = sigma, truncate =2.0)

    return u, v, ub, vb, mesh, dirs

def create_normals(
    img, 
    stride = 51, 
    win = 100, 
    tex_thresh = 40000
    ):
    '''
    Leaner version of vector field generator that only generates normals
    TODO: make this boiler plate in the vec field generator 
    '''

    N_y = img.shape[0]//stride + (-win)//stride
    N_x = img.shape[1]//stride + (-win)//stride

    dirs = np.zeros((N_y, N_x))

    #clip image at tex_thresh to enhance textures and remove high intensity noise
    clip_img = np.minimum(img, tex_thresh*np.ones(img.shape))
    hann = skimg.filters.window('hann', (win+1, win+1))
    for row in range(N_y):
        print('processing row {row} of {N_y}...'.format(row = row + 1, N_y = N_y))
        for col in range(N_x):
            scout = img[stride*row + win//2 - stride//2 : stride*row + win//2 + stride//2 + 1, stride*col + win//2 - stride//2 : stride*col + win//2 + stride//2 + 1]
            if np.mean(scout) > 0:
                #generate region of interest and analyse in frequency domain
                roi = clip_img[stride*row : stride*row + win+1, stride*col : stride*col + win+1]
                #roi = clip_img[stride*(row+1) : stride*(row+1) + win + 1, stride*(col+1) : stride*(col+1) + win+1]
                roi = roi * hann
                
                ft = np.abs(np.fft.fftshift(np.fft.fft2(roi)))
                
                r_max = 0.5*ft.shape[0]

                ftp = skimg.transform.warp_polar(ft, radius=r_max, output_shape=(180,20), center = (win/2, win/2))
                
                #identify dominant texture angle
                ang = np.sum(ftp, 1)
                ang = ang[0:90] + ang[90:180]
                #ang = moving_average(ang, 11) 
                ang = running_mean_uniform_filter1d(ang, 5)
                ang_max = np.argmax(ang);
                dirs[row, col] = 2*ang_max;

    print("done.")
    return dirs
##def main():
##    img = cv2.imread('06666mask.tif', cv2.IMREAD_UNCHANGED)
##    #u, v, ub, vb, mesh, dirs = create_vec_field(img)
##    print("loading u, v, ub, vb, and mesh...")
##    u       = np.load('u_0825.npy')
##    v       = np.load('v_0825.npy')
##    ub      = np.load('ub_0825.npy')
##    vb      = np.load('vb_0825.npy')
##    mesh    = np.load('mesh_0825.npy')
##    print("done.")
##
##    end_point     = (719, 1417) 
##    start_point   = (810, 2724)
##    #start   = (5851, 4420)
##    #end     = (4641, 5651)
##
##    sl1, sl2 = get_flowline(start_point, end_point, mesh[0], mesh[1], u, v, ub, vb, density = 100)
##    
##
##    # infill between stream pair using dsearchn to get a single line
##
##    # send that line to be plotted onto an image (instead of pon pyplot)
##
##    plt.subplot(1,2,1)
##    plt.imshow(img, cmap='gray')
##    plt.plot(sl1[:,0], sl1[:,1], color='r')
##
##    plt.subplot(1,2,2)
##    plt.imshow(img, cmap='gray')
##    plt.plot(sl2[:,0], sl2[:,1], color='b')
##    plt.show()
##    
##    '''
##    seed_points_b = np.array([[6546], [3691]])
##    plt.streamplot(mesh[0], mesh[1],ub, vb, integration_direction='forward', density=200, broken_streamlines=False, start_points=seed_points_b.T, color='b')
##    plt.imshow(img, cmap='gray')
##    plt.show()
##
##    '''
##    '''
##    with open('u_0825.npy', 'wb') as f:
##        np.save(f, u)
##
##    with open('v_0825.npy', 'wb') as f:
##        np.save(f, v)
##
##    with open('ub_0825.npy', 'wb') as f:
##        np.save(f, ub)
##
##    with open('vb_0825.npy', 'wb') as f:
##        np.save(f, vb)
##
##    with open('dirs_0825.npy', 'wb') as f:
##        np.save(f, dirs)
##
##    with open('mesh_0825.npy', 'wb') as f:
##        np.save(f, mesh)
##    '''
##
##    
##if __name__=='__main__':
##    main()
##    
