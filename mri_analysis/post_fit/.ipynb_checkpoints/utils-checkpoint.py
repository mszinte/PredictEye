def set_pycortex_config_file(data_folder):

    # Import necessary modules
    import os
    import cortex
    # import ipdb
    from pathlib import Path
    # deb = ipdb.set_trace

    # Define the new database and colormaps folder
    pycortex_db_folder = data_folder + '/pp_data/cortex/db/'
    pycortex_cm_folder = data_folder + '/pp_data/cortex/colormaps/'

    # Get pycortex config file location
    pycortex_config_file  = cortex.options.usercfg

    # Create name of new config file that will be written
    new_pycortex_config_file = pycortex_config_file[:-4] + '_new.cfg'

    # Create the new config file
    Path(new_pycortex_config_file).touch()

    # Open the config file in read mode and the newly created one in write mode.
    # Loop over every line in the original file and copy it into the new one.
    # For the lines containing either 'filestore' or 'colormap', it will
    # change the saved folder path to the newly created one above (e.g. pycortex_db_folder)
    with open(pycortex_config_file, 'r') as fileIn:
        with open(new_pycortex_config_file, 'w') as fileOut:

            for line in fileIn:

                if 'filestore' in line:
                    newline = 'filestore=' + pycortex_db_folder
                    fileOut.write(newline)
                    newline = '\n'

                elif 'colormaps' in line:
                    newline = 'colormaps=' + pycortex_cm_folder
                    fileOut.write(newline)
                    newline = '\n'

                else:
                    newline = line

                fileOut.write(newline)

    
    # Renames the original config file als '_old' and the newly created one to the original name
    os.rename(pycortex_config_file, pycortex_config_file[:-4] + '_old.cfg')
    os.rename(new_pycortex_config_file, pycortex_config_file)
    return None



def convert_fit_results(est_fn, output_fn, task, stim_width, stim_height):
    """
    Convert pRF or pMF fitting value in different parameters for following analysis
   
    Parameters
    ----------
    est_fn: absolute paths to estimates file
    output_fn: absolute path to derivative file
    stim_width: stimulus width in deg [for pRF only]
    stim_heigth: stimulus height in deg [for pRF only]

    Returns
    -------
    deriv: derivative of pRF/pMF analysis

    stucture output:
    columns: 1->size of input
    row00 : R2
    row01 : eccentricity in deg
    row02 : polar angle real component in deg
    row03 : polar angle imaginary component in deg
    row04 : size in deg
    row05 : amplitude
    row06 : baseline
    row07 : coverage or nan
    row08 : x
    row09 : y
    ['rsq','ecc','polar_real','polar_imag','size','amp','baseline','x','y','cov']
    """

    # Imports
    # -------
    # General imports
    import os
    import nibabel as nb
    import glob
    import numpy as np
    # import ipdb
    # deb = ipdb.set_trace
    
    # Popeye imports
    from popeye.spinach import generate_og_receptive_fields

    # Get data details
    # ----------------
    est = []
    img_est = nb.load(est_fn)
    est = img_est.get_fdata()

    # Compute derived measures from prfs/pmfs
    # ---------------------------------------
    # get data index
    x_idx, y_idx, sigma_idx, beta_idx, baseline_idx, rsq_idx = 0, 1, 2, 3, 4, 5

    # change to nan empty voxels
    est[est[:,:,:,rsq_idx] == 0] = np.nan
    
    # r-square
    rsq = est[:,:,:,rsq_idx]

    # eccentricity
    ecc = np.nan_to_num(np.sqrt(est[:,:,:,x_idx]**2 + est[:,:,:,y_idx]**2))

    # polar angle
    complex_polar = est[:,:,:,x_idx] + 1j * est[:,:,:,y_idx]
    normed_polar = complex_polar / np.abs(complex_polar)
    polar_real = np.real(normed_polar)
    polar_imag = np.imag(normed_polar)
    
    # size
    size_ = est[:,:,:,sigma_idx].astype(np.float64)
    size_[size_<1e-4] = 1e-4

    # amplitude
    amp = est[:,:,:,beta_idx]
    
    # baseline
    baseline = est[:,:,:,baseline_idx]

    # coverage
    if task=='pRF':
        deg_x, deg_y = np.meshgrid(np.linspace(-30, 30, 50), np.linspace(-30, 30, 50))         # define prfs in visual space
        flat_est = est.reshape((-1, est.shape[-1])).astype(np.float64)
        rfs = generate_og_receptive_fields( flat_est[:,x_idx],
                                            flat_est[:,y_idx],
                                            flat_est[:,sigma_idx],
                                            flat_est[:,beta_idx].T*0+1,
                                            deg_x,
                                            deg_y)

        total_prf_content = rfs.reshape((-1, flat_est.shape[0])).sum(axis=0)
        log_x = np.logical_and(deg_x >= -stim_width/2.0, deg_x <= stim_width/2.0)
        log_y = np.logical_and(deg_y >= -stim_height/2.0, deg_y <= stim_height/2.0)
        stim_vignet = np.logical_and(log_x,log_y)
        cov = rfs[stim_vignet, :].sum(axis=0) / total_prf_content
        cov = cov.reshape(baseline.shape)

    # x
    x = est[:,:,:,x_idx]

    # y
    y = est[:,:,:,y_idx]

    # Save results
    deriv = np.zeros((est.shape[0],est.shape[1],est.shape[2],10))*np.nan
    deriv[...,0]  = rsq
    deriv[...,1]  = ecc
    deriv[...,2]  = polar_real
    deriv[...,3]  = polar_imag
    deriv[...,4]  = size_
    deriv[...,5]  = amp
    deriv[...,6]  = baseline
    if task=='pRF':deriv[...,7]  = cov
    deriv[...,8]  = x
    deriv[...,9]  = y
        
    deriv = deriv.astype(np.float32)
    new_img = nb.Nifti1Image(dataobj = deriv, affine = img_est.affine, header = img_est.header)
    new_img.to_filename(output_fn)

    return None
    
def draw_cortex_vertex(subject,xfmname,data,vmin,vmax,description,volume_type='VolumeRGB',cmap='Viridis',cbar = 'discrete',cmap_steps = 255,\
                        alpha = None,depth = 1,thick = 1,height = 1024,sampler = 'nearest',\
                        with_curvature = True,with_labels = False,with_colorbar = False,\
                        with_borders = False,curv_brightness = 0.95,curv_contrast = 0.05,add_roi = False,\
                        roi_name = 'empty',col_offset = 0, zoom_roi = None, zoom_hem = None, zoom_margin = 0.0,):
    """
    Plot brain data onto a previously saved flatmap.
    Parameters
    ----------
    subject             : subject id (e.g. 'sub-001')
    xfmname             : xfm transform
    data                : the data you would like to plot on a flatmap
    cmap                : colormap that shoudl be used for plotting
    vmins               : minimal values of 1D 2D colormap [0] = 1D, [1] = 2D
    vmaxs               : minimal values of 1D/2D colormap [0] = 1D, [1] = 2D
    description         : plot title
    volume_type         : cortex function to create the volume (VolumeRGB or Volume2D)
    cbar                : color bar layout
    cmap_steps          : number of colormap bins
    alpha               : alpha map
    depth               : Value between 0 and 1 for how deep to sample the surface for the flatmap (0 = gray/white matter boundary, 1 = pial surface)
    thick               : Number of layers through the cortical sheet to sample. Only applies for pixelwise = True
    height              : Height of the image to render. Automatically scales the width for the aspect of the subject's flatmap
    sampler             : Name of sampling function used to sample underlying volume data. Options include 'trilinear', 'nearest', 'lanczos'
    with_curvature      : Display the rois, labels, colorbar, annotated flatmap borders, or cross-hatch dropout?
    with_labels         : Display labels?
    with_colorbar       : Display pycortex' colorbar?
    with_borders        : Display borders?
    curv_brightness     : Mean brightness of background. 0 = black, 1 = white, intermediate values are corresponding grayscale values.
    curv_contrast       : Contrast of curvature. 1 = maximal contrast (black/white), 0 = no contrast (solid color for curvature equal to curvature_brightness).
    add_roi             : add roi -image- to overlay.svg
    roi_name            : roi name
    col_offset          : colormap offset between 0 and 1
    zoom_roi            : name of the roi on which to zoom on
    zoom_hem            : hemifield fo the roi zoom
    zoom_margin         : margin in mm around the zoom
    Returns
    -------
    vertex_rgb - pycortex vertex file
    """
    
    import cortex
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.colors as colors
    from matplotlib import cm
    import matplotlib as mpl
    # import ipdb
    # deb = ipdb.set_trace
    
    # define colormap
    base = cortex.utils.get_cmap(cmap)
        
    if '_alpha' in cmap: base.colors = base.colors[1,:,:]
    val = np.linspace(0, 1,cmap_steps+1,endpoint=False)
    colmap = colors.LinearSegmentedColormap.from_list('my_colmap',base(val), N = cmap_steps)
    
    if volume_type=='VolumeRGB':
        # convert data to RGB
        vrange = float(vmax) - float(vmin)
        norm_data = ((data-float(vmin))/vrange)*cmap_steps
        mat = colmap(norm_data.astype(int))*255.0
        alpha = alpha*255.0

        # define volume RGB

        volume = cortex.VolumeRGB(  channel1 = mat[...,0].T.astype(np.uint8),
                                    channel2 = mat[...,1].T.astype(np.uint8),
                                    channel3 = mat[...,2].T.astype(np.uint8),
                                    alpha = alpha.T.astype(np.uint8),
                                    subject = subject,
                                    xfmname = xfmname)
    elif volume_type=='Volume2D':
        volume = cortex.Volume2D(dim1 = data.T,
                                 dim2 = alpha.T,
                                 subject = subject,
                                 xfmname = xfmname,
                                 description = description,
                                 cmap = cmap,
                                 vmin = vmin[0],
                                 vmax = vmax[0],
                                 vmin2 = vmin[1],
                                 vmax2 = vmax[1])
    
    volume_fig = cortex.quickshow(  braindata = volume,
                                    depth = depth,
                                    thick = thick,
                                    height = height,
                                    sampler = sampler,
                                    with_curvature = with_curvature,
                                    with_labels = with_labels,
                                    with_colorbar = with_colorbar,
                                    with_borders = with_borders,
                                    curvature_brightness = curv_brightness,
                                    curvature_contrast = curv_contrast)

   
    if cbar == 'polar':
        
        base = cortex.utils.get_cmap(cmap)
        val = np.arange(1,cmap_steps+1)/cmap_steps - (1/(cmap_steps*2))
        val = np.fmod(val+col_offset,1)
        colmap = colors.LinearSegmentedColormap.from_list('my_colmap',base(val),N = cmap_steps)

        cbar_axis = volume_fig.add_axes([0.5, 0.07, 0.8, 0.2], projection='polar')
        norm = colors.Normalize(0, 2*np.pi)
        t = np.linspace(0,2*np.pi,200,endpoint=True)
        r = [0,1]
        rg, tg = np.meshgrid(r,t)
        im = cbar_axis.pcolormesh(t, r, tg.T,norm= norm, cmap = colmap)
        cbar_axis.set_yticklabels([])
        cbar_axis.set_xticklabels([])
        cbar_axis.set_theta_zero_location("W")

        cbar_axis.spines['polar'].set_visible(False)

    elif cbar == 'ecc':
        
        # Ecc color bar
        colorbar_location = [0.5, 0.07, 0.8, 0.2]
        n = 200
        cbar_axis = volume_fig.add_axes(colorbar_location, projection='polar')

        t = np.linspace(0,2*np.pi, n)
        r = np.linspace(0,1, n)
        rg, tg = np.meshgrid(r,t)
        c = tg
            
        im = cbar_axis.pcolormesh(t, r, c, norm = mpl.colors.Normalize(0, 2*np.pi), cmap = colmap)
        cbar_axis.tick_params(pad = 1,labelsize = 15)
        cbar_axis.spines['polar'].set_visible(False)
            
        # superimpose new axis for dva labeling
        box = cbar_axis.get_position()
        cbar_axis.set_yticklabels([])
        cbar_axis.set_xticklabels([])
        axl = volume_fig.add_axes(  [1.8*box.xmin,
                                        0.5*(box.ymin+box.ymax),
                                        box.width/600,
                                        box.height*0.5])
        axl.spines['top'].set_visible(False)
        axl.spines['right'].set_visible(False)
        axl.spines['bottom'].set_visible(False)
        axl.yaxis.set_ticks_position('right')
        axl.xaxis.set_ticks_position('none')
        axl.set_xticklabels([])
        axl.set_yticklabels(np.linspace(vmin,vmax,3),size = 'x-large')
        axl.set_ylabel('$dva$\t\t', rotation = 0, size = 'x-large')
        axl.yaxis.set_label_coords(box.xmax+30,0.4)
        axl.patch.set_alpha(0.5)

    elif cbar == 'discrete':

        # Discrete color bars
        # -------------------
        colorbar_location= [0.9, 0.05, 0.03, 0.25]
        cmaplist = [colmap(i) for i in range(colmap.N)]

        # define the bins and normalize
        bounds = np.linspace(vmin, vmax, cmap_steps + 1) if volume_type=='VolumeRGB' else np.linspace(vmin[0], vmax[0], cmap_steps + 1)
        bounds_label = np.linspace(vmin, vmax, 3) if volume_type=='VolumeRGB' else np.linspace(vmin[0], vmax[0], 3)
        norm = mpl.colors.BoundaryNorm(bounds, colmap.N)
            
        cbar_axis = volume_fig.add_axes(colorbar_location)
        cb = mpl.colorbar.ColorbarBase(cbar_axis,cmap = colmap,norm = norm,ticks = bounds_label,boundaries = bounds)

    # add to overalt
    if add_roi == True:
        cortex.utils.add_roi(   data = volume,
                                name = roi_name,
                                open_inkscape = False,
                                add_path = False,
                                depth = depth,
                                thick = thick,
                                sampler = sampler,
                                with_curvature = with_curvature,
                                with_colorbar = with_colorbar,
                                with_borders = with_borders,
                                curvature_brightness = curv_brightness,
                                curvature_contrast = curv_contrast)

    return volume

def mask_nifti_2_hdf5(deriv_file, tc_file, mask_file_L, mask_file_R, hdf5_file, model, folder_alias):
    """
    masks data in in_file with mask in mask_file,
    to be stored in an hdf5 file
    Takes a 4D fMRI nifti-files and masks the
    data with the mask in mask_file.
    
    Parameters
    ----------
    in_files : absolute path to functional nifti-file
    mask_file_L : absolute path to LH mask nifti-file 
    mask_file_R : absolute path to RH mask nifti-file 
    hdf5_file : absolute path to hdf5 file.
    model : pRF model
    folder_alias : name of the to-be-created folder in the hdf5 file.
    
    Returns
    -------
    None
    """

    import nibabel as nb
    import numpy as np
    import h5py
    # import ipdb
    import os
    # deb = ipdb.set_trace

    # load deriv file to mask
    deriv_file_img = nb.load(deriv_file)
    deriv_file_data = deriv_file_img.get_fdata()

    # load tc file to mask
    tc_file_img = nb.load(tc_file)
    tc_file_data = tc_file_img.get_fdata()
    
    # load masks
    mask_file_L_img = nb.load(mask_file_L)
    mask_file_L_data = mask_file_L_img.get_fdata()
    mask_file_R_img = nb.load(mask_file_R)
    mask_file_R_data = mask_file_R_img.get_fdata()
    # mask_file_data = mask_file_L_data + mask_file_R_data
    
    
    # coordinates
    coord_mask_L = np.array(np.where(mask_file_L_data == True)).T
    coord_mask_R = np.array(np.where(mask_file_R_data == True)).T
    coord_mask = np.vstack((coord_mask_L,coord_mask_R))
    
    # deriv + add hemi val (LH = 1; RH = 2)
    deriv_mask_L_data = deriv_file_data[mask_file_L_data == True,:]
    deriv_mask_L_data = np.hstack((deriv_mask_L_data,np.ones((deriv_mask_L_data.shape[0],1)) * 1.0))
    deriv_mask_R_data = deriv_file_data[mask_file_R_data == True,:]
    deriv_mask_R_data = np.hstack((deriv_mask_R_data,np.ones((deriv_mask_R_data.shape[0],1)) * 2.0))
    deriv_mask_data = np.vstack((deriv_mask_L_data,deriv_mask_R_data))

    # time course
    tc_mask_L_data = tc_file_data[mask_file_L_data == True,:]
    tc_mask_R_data = tc_file_data[mask_file_R_data == True,:]
    tc_mask_data = np.vstack((tc_mask_L_data,tc_mask_R_data))

    # model time course
    rsq_idx, ecc_idx, polar_real_idx, polar_imag_idx , size_idx, \
            amp_idx, baseline_idx, cov_idx, x_idx, y_idx = 0,1,2,3,4,5,6,7,8,9
    tc_model_mask_data = np.zeros(tc_mask_data.shape)*np.nan
       
    for i in np.arange(0,tc_model_mask_data.shape[0]):
        if np.isnan(deriv_mask_data[i,rsq_idx]):
            pass
        else:
            tc_model_mask_data[i,:] = model.return_prediction(mu_x = deriv_mask_data[i,x_idx],
                                                              mu_y = deriv_mask_data[i,y_idx], 
                                                              size = deriv_mask_data[i,size_idx],
                                                              beta = deriv_mask_data[i,amp_idx],
                                                              baseline = deriv_mask_data[i,baseline_idx])

    try:
        h5file = h5py.File(hdf5_file, "r+")
    except:
        h5file = h5py.File(hdf5_file, "a")
    
    try:
        h5file.create_group(folder_alias)
    except:
        None

    h5file.create_dataset(  '{folder_alias}/derivatives'.format(folder_alias = folder_alias),
                            data = deriv_mask_data,
                            dtype ='float32')

    h5file.create_dataset(  '{folder_alias}/time_course'.format(folder_alias = folder_alias),
                            data = tc_mask_data,
                            dtype ='float32')
    h5file.create_dataset(  '{folder_alias}/time_course_model'.format(folder_alias = folder_alias),
                            data = tc_model_mask_data,
                            dtype ='float32')
    h5file.create_dataset(  '{folder_alias}/coord'.format(folder_alias = folder_alias),
                            data = coord_mask,
                            dtype ='float32')

    
    return None


def eventsMatrix(design_file):
    """
    Returns the events matrix for the GLM. Works for the Sac/Pur Localisers and Sac/Pur Visual/Endogenous Localisers
    Parameters
    ----------
    design_file         : path to the tsv file
    Returns
    -------
    new_events_glm - pandas DataFrame containing the events for the GLM 
    """
    
    tr_dur = 1.2
    events = pd.read_table(design_file)

    if 'VE' not in task: # Sac/Pur Loc
        events_glm = events[['onset','duration','trial_type']].copy(deep=True)
        events_glm.replace({'trial_type': {3: 'Fix', 1: 'Sac', 2: 'Pur'}},inplace=True)
        events_glm.at[:,'duration'] = tr_dur
        events_glm.at[:,'onset'] = 0
        events_glm_groups = events_glm.groupby((events_glm.trial_type!=events_glm.trial_type.shift()).cumsum())

        new_events_glm = pd.DataFrame([], columns=['onset', 'duration', 'trial_type'])
        for idx, group in enumerate(events_glm_groups):
            onset = group[1]['onset'][group[1].index[0]]
            dur = sum(group[1]['duration'])
            ttype = group[1]['trial_type'][group[1].index[0]]

            new_events_glm = new_events_glm.append(pd.Series([onset,dur,ttype],index =['onset', 'duration', 'trial_type']), ignore_index=True)

    else: # Visual-Endogenous Sac/Pur Loc    
        events_glm = events[['onset','duration','trial_type', 'eyemov_vis_end']].copy(deep=True)
        events_glm.replace({'trial_type': {3: 'Fix', 1: 'Sac', 2: 'Pur'}},inplace=True)
        events_glm.replace({'eyemov_vis_end': {3: 'Fix', 1: 'Vis', 2: 'End'}},inplace=True)
        events_glm.at[:,'duration'] = tr_dur
        events_glm.at[:,'onset'] = 0
        events_glm_groups = events_glm.groupby((events_glm.eyemov_vis_end!=events_glm.eyemov_vis_end.shift()).cumsum())

        new_events_glm = pd.DataFrame([], columns=['onset', 'duration', 'trial_type', 'vis_end'])
        for idx, group in enumerate(events_glm_groups):
            onset = group[1]['onset'][group[1].index[0]]
            dur = sum(group[1]['duration'])
            ttype = group[1]['trial_type'][group[1].index[0]]
            vis_end = group[1]['eyemov_vis_end'][group[1].index[0]]

            new_events_glm = new_events_glm.append(pd.Series([onset,dur,vis_end],index =['onset', 'duration', 'trial_type']), ignore_index=True)

    for idx in new_events_glm.index:
        if idx==0:
            new_events_glm.at[idx, 'onset'] = int(0)
        else:
            new_events_glm.at[idx, 'onset'] = new_events_glm.at[idx-1, 'onset'] + new_events_glm.at[idx-1, 'duration']

    return new_events_glm

