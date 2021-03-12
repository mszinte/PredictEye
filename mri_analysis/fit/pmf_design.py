"""
-----------------------------------------------------------------------------------------
pmf_design.py
-----------------------------------------------------------------------------------------
Goal of the script:
Create pMF motor design for fit
-----------------------------------------------------------------------------------------
Input(s):
none
-----------------------------------------------------------------------------------------
Output(s):
.mat design files in pp_data/visual_dm/
-----------------------------------------------------------------------------------------
To run:
cd /home/mszinte/projects/PredictEye/mri_analysis/
python pmf_design.py
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com)
-----------------------------------------------------------------------------------------
"""

import numpy as np
from PIL import Image 
import itertools, json
import scipy.io

# Define analysis parameters
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# define parameters
base_dir = analysis_info['base_dir']                            # data directory
sub_tasks = analysis_info['sub_task_list'][1:2]                 # trs during break period
trs_break = analysis_info['trs_break']                          # trs during break period
trs_eye_mov = analysis_info['trs_eye_mov']                      # trs during eye movement period
ppd = analysis_info['ppd']                                      # nb of pixels per degrees
TRs = analysis_info['TRs']                                      # total number of TR
screen_width_px = analysis_info['screen_width_px']              # screen width in pixel
screen_height_px = analysis_info['screen_height_px']            # screen height in pixel
eye_mov_height_dva = analysis_info['eye_mov_height_dva']        # eye movement are height in dva
pix_ratio = analysis_info['pix_ratio']                          # ratio of pixel motor design for later fit
ratio_out = eye_mov_height_dva/(screen_height_px/ppd)           # ratio to compute of out of screen pixel size eye movement can be made
screen = [screen_width_px,screen_height_px]                     # screen resolution in pixels (use height of pRF)
screen = [int(screen[0]*ratio_out),int(screen[1]*ratio_out)]    # screen recomputed size
center = [screen[0]/2,screen[1]/2]                              # screen center 
dir_sp = np.deg2rad(np.arange(0,360,22.5))                      # smooth pursuit directions in radian
dir_sac = np.deg2rad(np.arange(0,360,22.5)+180)                 # saccade directions in radian
sp_amp = analysis_info['sp_amp']*ppd                            # smooth pursuit amplitude/speed
sac_amp = analysis_info['sac_amp']*ppd                          # saccade amplitude
sp_radial_sd = analysis_info['sp_radial_sd']                    # list of smooth pursuit radial std gaussian          
sp_tangential_sd = analysis_info['sp_tangential_sd']            # list of smooth pursuit tangential std gaussian
sac_radial_sd = analysis_info['sac_radial_sd']                  # list of saccade radial std gaussian
sac_tangential_sd = analysis_info['sac_tangential_sd']          # list of saccade tangential std gaussian
sigma_sp  =[[sp_radial_sd[0]*ppd, sp_tangential_sd[0]*ppd],     # smooth pursuit area sd for first amplitude
            [sp_radial_sd[1]*ppd, sp_tangential_sd[1]*ppd],     # smooth pursuit area sd for second amplitude
            [sp_radial_sd[2]*ppd, sp_tangential_sd[2]*ppd],     # smooth pursuit area sd for third amplitude
            [sp_radial_sd[3]*ppd, sp_tangential_sd[3]*ppd]]     # smooth pursuit area sd for fourth amplitude
sigma_sac =[[sac_radial_sd[0]*ppd, sac_tangential_sd[0]*ppd],   # saccade area sd for first amplitude
            [sac_radial_sd[1]*ppd, sac_tangential_sd[1]*ppd],   # saccade area sd for second amplitude
            [sac_radial_sd[2]*ppd, sac_tangential_sd[2]*ppd],   # saccade area sd for third amplitude
            [sac_radial_sd[3]*ppd, sac_tangential_sd[3]*ppd]]   # saccade area sd for fourth amplitude

def compute_screen(screen, sigma, mu, rot):
    """
    Compute motor design screen as non isotropic gaussian fields

    Parameters
    ----------
    screen : array (2D)
        screen width [0] and height [1] in pixel
    
    sigma : array (2D)
        gaussian field radial [0] and tangential [1] standard deviation
    
    mu : array (2D)
        center x [0] and y [1] of the gaussian

    rot: array (1D)
        rotation angle in radian of the gaussian main axis

    Returns
    -------
    z_col: meshgrid of the screen
    """
    x, y = np.meshgrid(np.arange(0,screen[0],1), np.arange(0,screen[1],1))
    x,y = x - mu[0], y - mu[1]
    rot_mat = np.array([[np.cos(rot), np.sin(rot)],
                        [-np.sin(rot), np.cos(rot)]])
    mult = np.dot(rot_mat, np.array([x.ravel(),y.ravel()]))
    x = mult[0,:].reshape(x.shape)
    y = mult[1,:].reshape(y.shape)
    z = (1/(2*np.pi*sigma[0]*sigma[1]) * np.exp(-((x)**2/(2*sigma[0]**2) + (y)**2/(2*sigma[1]**2))))
    z_norm = (z - np.min(z)) / (np.max(z) - np.min(z))
    z_col = np.round(z_norm*255)
    
    return z_col

print('compute images')
for sub_task in sub_tasks:
    permut = itertools.permutations([1, 2, 3, 4])
    seq_num = 1
    for eachpermutation in permut:
        seq_order = [5,eachpermutation[0],5,eachpermutation[1],5,eachpermutation[2],5,eachpermutation[3],5]
        stim = np.zeros((int(screen[1]),int(screen[0]),TRs))
        tr_num = 0
        eyemov_num = 0

        for seq in seq_order:
            if seq == 5:
                for tr in np.arange(0,trs_break,1):
                    # make blank image
                    stim[:,:,tr_num] = np.zeros((screen[1],screen[0]))
                    tr_num += 1
            else:
                num_sp, num_sac = 0, 0
                for tr in np.arange(0,trs_eye_mov,1):
                    if np.mod(tr,2)==False:
                        if sub_task == 'sp':
                            # get sp center coordinate in retinal coordinates
                            mu = [center[0] + np.cos(dir_sp[num_sp])*sp_amp[seq-1], center[1] - np.sin(dir_sp[num_sp])*sp_amp[seq-1]]
                            rot = -dir_sp[num_sp]
                            sigma = sigma_sp[seq-1]
                            stim[:,:,tr_num] = compute_screen(screen, sigma, mu, rot)
                            num_sp += 1
                        else:
                            stim[:,:,tr_num] = np.zeros((screen[1],screen[0]))
                        tr_num += 1
                        
                    else:
                        if sub_task == 'sac': 
                            # get saccade center coordinate in retinal coordinates
                            mu = [center[0] + np.cos(dir_sac[num_sac])*sac_amp[seq-1], center[1] - np.sin(dir_sac[num_sac])*sac_amp[seq-1]]
                            rot = -dir_sac[num_sac]
                            sigma = sigma_sac[seq-1]
                            stim[:,:,tr_num] = compute_screen(screen, sigma, mu, rot)
                            num_sac += 1
                        else:
                            stim[:,:,tr_num] = np.zeros((screen[1],screen[0]))
                        tr_num += 1

        # resize it for fit
        screen_resize = [int(screen[0]*pix_ratio),int(screen[1]*pix_ratio)]
        center_resize = [screen_resize[0]/2,screen_resize[1]/2]
        stim_resize = np.zeros([screen_resize[0],screen_resize[1],TRs])
        for tr in np.arange(0,TRs,1):
            stim_resize[:,:,tr] = np.array(Image.fromarray(stim[:,:,tr]).convert('RGB').resize(size=screen_resize))[:,:,0]

        mat_dict = {'sequence': seq_order,
                    'stim': stim_resize}

        mat_file_name = "{}/pp_data/visual_dm/pMF{}_vd_seq{}.mat".format(base_dir, sub_task, seq_num)
        scipy.io.savemat(file_name=mat_file_name, mdict=mat_dict, do_compression=True)
        print("subtask: {}, permutation : {} = done".format(sub_task,seq_num))
        seq_num += 1