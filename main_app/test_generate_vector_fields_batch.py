print("take a directory of .tif files, and generate name-matched .npy files for each of them")

'''
unused code; requires automated origin detection beforei it can be included in pipeline
'''


import numpy as np
import skimage as skimg
import cv2
import os
import scipy.ndimage as ndi
import collections
import pandas as pd



def create_vec_field(
    img, 
    stride      = 3, 
    win         = 100, 
    tex_thresh  = 40000, 
    pap_thresh  = 30000, 
    origin      = [0,0], #TODO: make this selectable
    sub_angles  = 6,
    alpha_v     = 7e-5,
    sigma_v     = 2.0,
    alpha_p     = 5.0,
    beta_p      = 2.0,
    gamma_p     = 0.3,
    delta_p     = 1.4,
    sigma       = 3.0
    ):
    '''
    generates a vector field to trace papyrus layers based on textural and contextual information in img
    stride     = downsampling factor (higher runs faster but is less accurate)
    win        = window size for regions around query pixels (higher is slower but less noisy and less accurate)
    tex_thresh = threshold above which textures are to be ignored
    pap_thresh = threshold between papyrus and void
    origin     = rotational center of layer, as tuple
    sub_angles = number of angular subdivisions for directional blur
    alpha_v    = scaling factor for avoiding void when tracing
    sigma_v    = region of influence for void avoidance effect
    alpha_p    = region of influence for boundary tracing effect
    beta_p     = region of zero influence for boundary tracing effect
    gamma_p    = scaling factor for boundary tracing effect
    delta_p    = whether boundary tracing force is attractive or repulsive, 1 is neutral
    sigma      = size of smoothing kernel for resultant vector field
    '''

    N_y = img.shape[0]//stride + (-win)//stride
    N_x = img.shape[1]//stride + (-win)//stride

    dirs = np.zeros((N_y, N_x))

    #clip image at tex_thresh to enhance textures and remove high intensity noise
    clip_img = np.minimum(img, tex_thresh*np.ones(img.shape))

    for row in range(N_y):
        print("\tprocessing row {row} of {N_y}...".format(row = row + 1, N_y = N_y))
        for col in range(N_x):
            scout = img[stride*row + win//2 - stride//2 : stride*row + win//2 + stride//2 + 1, stride*col + win//2 - stride//2 : stride*col + win//2 + stride//2 + 1]
            if np.mean(scout) > 0:
                #generate region of interest and analyse in frequency domain
                roi = clip_img[stride*row : stride*row + win+1, stride*col : stride*col + win+1]
                #roi = clip_img[stride*(row+1) : stride*(row+1) + win + 1, stride*(col+1) : stride*(col+1) + win+1]
                roi = roi * skimg.filters.window('hann', roi.shape)
                
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


class OriginSlector(object):
    def __init__(self, img, window_name="image"):
        self.window_name = window_name
        self.img_base = img
        self.img_view = self.img_base.copy()
        self.origin_location = []
        
        cv2.imshow(self.window_name,self.img_view)
        cv2.setMouseCallback(self.window_name, self.click_event)
    def click_event(self, event, x, y, flags, params):
        # checking for left mouse clicks        
        if event == cv2.EVENT_LBUTTONDOWN:
            print("proposed origin: "+str([x,y]))
            self.origin_location = [x,y]
            self.update_display()
        
    def update_display(self):
        self.img_view = self.img_base.copy()       
        cv2.circle(self.img_view, self.origin_location, 10, (0,0,255),2)
        cv2.imshow(self.window_name,self.img_view)

        
def batch_generate_vector_fields(path_to_image_slice_input, path_to_vector_field_output, stride = 3, win = 100, tex_thresh = 40000, pap_thresh = 30000, sub_angles = 6, alpha_v = 7e-5, sigma_v = 2.0, alpha_p = 5.0, beta_p = 2.0, gamma_p = 0.3, delta_p = 1.4, sigma = 3.0):
    # add seperators characters if not present in path names 
    if not path_to_image_slice_input.endswith("\\"):
        path_to_image_slice_input += "\\"
    if not path_to_vector_field_output.endswith("\\"):
        path_to_vector_field_output += "\\"


    # check files in input directory for correctness    
    list_of_files_to_process = os.listdir(path_to_image_slice_input)
    #print("list_of_files_to_process: "+str(list_of_files_to_process))
    list_of_files_to_process = [file for file in list_of_files_to_process if file.endswith(".tif")]
    if not all(file.split(".")[0].isnumeric() for file in list_of_files_to_process):
        print("WARNING: image slice filenames must be numeric for use in VolumeAnnotate.  The following files will not be processed: ")
        list_of_excluded_files = [file for file in list_of_files_to_process if file.split(".")[0].isnumeric() == False]
        print(list_of_excluded_files)
    list_of_files_to_process = [file for file in list_of_files_to_process if file.split(".")[0].isnumeric() == True]
    #print("list_of_files_to_process: "+str(list_of_files_to_process))

    
    # select origin for each slice by clicking
    print("select origin for the following slices by clicking on the innermost part of the scroll (approximate location is ok).  \nPress the \"Esc\" key to move on to next slice")
    origin_list = []
    for file in list_of_files_to_process:
        img = cv2.imread(path_to_image_slice_input+file, cv2.IMREAD_UNCHANGED)
        window_name = str(path_to_image_slice_input+file)

        window = OriginSlector(img, window_name=window_name)
        key = -1
        while key != ord('k') and key != 27:

            key = cv2.waitKey(0)

        origin = window.origin_location
        cv2.destroyAllWindows()

        if origin == []:
            print("WARNING: no origin selected for "+str(file)+", vector field will use center coordinates by default")
            origin = [int(img.shape[0]/2),int(img.shape[1]/2)]
        else:
            print("origin for "+str(file)+": "+str(origin))
        origin_list.append(origin)
    print("origin_list: "+str(origin_list))

    # iteratively call create_vec_field for each file
    
    for i in range(len(list_of_files_to_process)):
        file = list_of_files_to_process[i]
        origin = origin_list[i]

        print("generating vectors for: "+str(path_to_image_slice_input+file)+"...")
        img = cv2.imread(path_to_image_slice_input+file, cv2.IMREAD_UNCHANGED)
        # latter _,_ are mesh, dir
        u, v, ub, vb, _, _ = create_vec_field(img, stride = stride, win = win, tex_thresh = tex_thresh, pap_thresh = pap_thresh, origin =  origin, sub_angles = sub_angles, alpha_v = alpha_v, sigma_v = sigma_v, alpha_p = alpha_p, beta_p = beta_p, gamma_p = gamma_p, delta_p = delta_p, sigma = sigma)    
        print("done.")

        print("saving vector field...")
        with open(path_to_vector_field_output+file.split(".")[0]+".npy", "wb") as f:
            # cast from 32bit to 16bit precision on output
            stack = np.stack([u, v, ub, vb], dtype=np.float16)
            np.save(f, stack)

        print("done.")

        # write u, v, ub, vb, mesh, and dirs to single .npy file
        #print("u: "+str(u))

    
##        
##def main():
##    path_to_image_slice_input = "image_slice_input\\"
##    path_to_vector_field_output = "vector_field_output\\"
##
##    batch_generate_vector_fields(path_to_image_slice_input, path_to_vector_field_output, stride = 3, win = 100, tex_thresh = 40000, pap_thresh = 30000, sub_angles = 6, alpha_v = 7e-5, sigma_v = 2.0, alpha_p = 5.0, beta_p = 2.0, gamma_p = 0.3, delta_p = 1.4, sigma = 3.0)
##
##if __name__ == "__main__":
##    main()
