def eventsMatrix(design_file, task):
    """
    Returns the events matrix for the GLM. Works for the Sac/Pur Localisers and Sac/Pur Visual/Endogenous Localisers
    Parameters
    ----------
    design_file         : path to the tsv/csv file containing the events
    task                : task name (SacLoc / PurLoc / SacVELoc / PurVELoc)
    Returns
    -------
    new_events_glm - pandas DataFrame containing the events for the GLM 
    """
    import pandas as pd
    
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
    import ipdb
    
    deb = ipdb.set_trace
    
    # define colormap
    try:
        base = plt.cm.get_cmap(cmap)
    except:
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