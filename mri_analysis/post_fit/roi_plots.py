"""
-----------------------------------------------------------------------------------------
roi_plots.py
-----------------------------------------------------------------------------------------
Goal of the script:
Draw roi plots (maps, ecc vs. params, laterality, time course)
-----------------------------------------------------------------------------------------
Input(s):
sys.argv[1]: subject name (e.g. 'sub-001')
sys.argv[2]: task (ex: GazeCenterFS)
sys.argv[3]: pre-processing steps (fmriprep_dct or fmriprep_dct_pca)
sys.argv[4]: save SVG figures (0 = No, 1 = Yes)
-----------------------------------------------------------------------------------------
Output(s):
HTML figures
-----------------------------------------------------------------------------------------
To run:
>> cd to function
>> python post_fit/roi_plots.py [subject] [task] [preproc] [svg]
-----------------------------------------------------------------------------------------
Exemple:
cd /home/mszinte/projects/pRFgazeMod/mri_analysis/
python post_fit/roi_plots.py sub-001 GazeCenterFS fmriprep_dct 0
-----------------------------------------------------------------------------------------
Written by Martin Szinte (martin.szinte@gmail.com)
-----------------------------------------------------------------------------------------
"""

# Stop warnings
# -------------
import warnings
warnings.filterwarnings("ignore")

# General imports
# ---------------
import os
import sys
import json
import glob
import numpy as np
import matplotlib.pyplot as pl
import ipdb
import platform
import h5py
import scipy.io
opj = os.path.join
deb = ipdb.set_trace

# MRI imports
# -----------
import nibabel as nb
import cortex

# Functions import
# ----------------
from plot_class import PlotOperator
from utils import set_pycortex_config_file

# Bokeh imports
# ---------------
from bokeh.io import output_notebook, show, save, output_file, export_png, export_svgs
from bokeh.layouts import row, column, gridplot

# Get inputs
# ----------
subject = sys.argv[1]
task = sys.argv[2]
preproc = sys.argv[3]
save_svg = int(sys.argv[4])

# Define analysis parameters
# --------------------------
with open('settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# Define folders and settings
# ---------------------------
base_dir = analysis_info['base_dir']
rois = analysis_info['rois']
sample_ratio = analysis_info['sample_ratio']
deriv_dir = "{base_dir}/pp_data/{subject}/gauss/deriv".format(base_dir = base_dir, subject = subject)
h5_dir = "{base_dir}/pp_data/{subject}/gauss/h5".format(base_dir = base_dir, subject = subject)
bokeh_dir = "{base_dir}/pp_data/{subject}/gauss/bokeh_outputs".format(base_dir = base_dir, subject = subject)
try: os.makedirs(bokeh_dir)
except: pass

# Draw main analysis figure
# -------------------------
print('creating bokeh plots')
rsq_idx, ecc_idx, polar_real_idx, polar_imag_idx , size_idx, \
    amp_idx, baseline_idx, cov_idx, x_idx, y_idx, hemi_idx = 0,1,2,3,4,5,6,7,8,9,10

# Initialize data
# ---------------
for roi_num, roi in enumerate(rois):
    
    # create html folder
    exec("html_dir = '{bokeh_dir}/html/{task}_{preproc}/'".format(bokeh_dir = bokeh_dir, task = task, preproc = preproc))
    try: os.makedirs(html_dir)
    except: pass

    # create svg folder
    if save_svg == 1:
        exec("svg_dir = '{bokeh_dir}/svg/'".format(bokeh_dir = bokeh_dir))
        try: os.makedirs(svg_dir)
        except: pass

    # load h5 file
    h5_file = h5py.File("{h5_dir}/{roi}_{task}_{preproc}.h5".format(h5_dir = h5_dir, roi = roi, task = task, preproc = preproc),'r')

    # load deriv data
    deriv_data = h5_file['{folder_alias}/derivatives'.format(folder_alias = 'pRF')]
    
    # load time course data
    tc_data = h5_file['{folder_alias}/time_course'.format(folder_alias = 'pRF')]

    # load model time course data
    tc_model_data = h5_file['{folder_alias}/time_course_model'.format(folder_alias = 'pRF')]

    # load coordinates data
    coord_data = h5_file['{folder_alias}/coord'.format(folder_alias = 'pRF')]

    # threshold data
    voxel_num_ini = deriv_data.shape[0]
    voxel_num = 0
    if voxel_num_ini > 0:
        # take out nan
        tc_data = tc_data[~np.isnan(deriv_data[:,rsq_idx]),:]
        tc_model_data = tc_model_data[~np.isnan(deriv_data[:,rsq_idx]),:]
        coord_data = coord_data[~np.isnan(deriv_data[:,rsq_idx]),:]
        deriv_data = deriv_data[~np.isnan(deriv_data[:,rsq_idx]),:]

        # threshold on eccentricity and size
        deriv_data_th = deriv_data
        rsqr_th = deriv_data_th[:,rsq_idx] >= analysis_info['rsqr_th']
        size_th_down = deriv_data_th[:,size_idx] >= analysis_info['size_th'][0]
        size_th_up = deriv_data_th[:,size_idx] <= analysis_info['size_th'][1]
        ecc_th_down = deriv_data_th[:,ecc_idx] >= analysis_info['ecc_th'][0]
        ecc_th_up = deriv_data_th[:,ecc_idx] <= analysis_info['ecc_th'][1]
        all_th = np.array((rsqr_th,size_th_down,size_th_up,ecc_th_down,ecc_th_up)) 

        deriv_data = deriv_data[np.logical_and.reduce(all_th),:]
        tc_data = tc_data[np.logical_and.reduce(all_th),:]
        tc_model_data = tc_model_data[np.logical_and.reduce(all_th),:]
        coord_data = coord_data[np.logical_and.reduce(all_th),:]
        voxel_num = deriv_data.shape[0]
        
    # Draw and save figures
    # ---------------------
    if voxel_num > 0:
        # randomize order and take 10 %
        new_order = np.random.permutation(voxel_num)
        deriv_data = deriv_data[new_order,:]
        tc_data = tc_data[new_order,:]
        tc_model_data = tc_model_data[new_order,:]
        coord_data = coord_data[new_order,:]
        deriv_data_sample = deriv_data[0:int(np.round(voxel_num*sample_ratio)),:]

        print("drawing {roi}_{task}_{preproc} figures, n = {voxel_num}".format(roi = roi, voxel_num = voxel_num, task = task, preproc = preproc)) 

        data_source = { 'rsq': deriv_data[:,rsq_idx],
                        'ecc': deriv_data[:,ecc_idx],
                        'sigma': deriv_data[:,size_idx],
                        'beta': deriv_data[:,amp_idx],
                        'baseline': deriv_data[:,baseline_idx],
                        'cov': deriv_data[:,cov_idx],
                        'x': deriv_data[:,x_idx],
                        'y': deriv_data[:,y_idx],
                        'colors_ref': deriv_data[:,ecc_idx]}
        
        data_source_sample = { 
                        'rsq': deriv_data_sample[:,rsq_idx],
                        'ecc': deriv_data_sample[:,ecc_idx],
                        'sigma': deriv_data_sample[:,size_idx],
                        'beta': deriv_data_sample[:,amp_idx],
                        'baseline': deriv_data_sample[:,baseline_idx],
                        'cov': deriv_data_sample[:,cov_idx],
                        'x': deriv_data_sample[:,x_idx],
                        'y': deriv_data_sample[:,y_idx],
                        'colors_ref': deriv_data_sample[:,ecc_idx]}

        param_all = {   'roi_t': roi, 
                        'p_width': 400, 
                        'p_height': 400, 
                        'min_border_large': 10, 
                        'min_border_small': 5,
                        'bg_color': tuple([229,229,229]), 
                        'stim_color': tuple([250,250,250]), 
                        'hist_fill_color': tuple([255,255,255]),
                        'hist_line_color': tuple([0,0,0]), 
                        'stim_height': analysis_info['stim_height'],
                        'stim_width': analysis_info['stim_width'],
                        'cmap': 'Spectral',
                        'cmap_steps': 15,
                        'col_offset': 0,
                        'vmin': 0,
                        'vmax': 15,
                        'leg_xy_max_ratio': 1.8,
                        'dataMat': deriv_data,
                        'data_source': data_source,
                        'data_source_sample': data_source_sample,
                        'hist_range': (0,0.5),
                        'hist_steps': 0.5,
                        'h_hist_bins': 16,
                        'link_x': False,
                        'link_y': False,
                        'save_svg': save_svg
                        }

        if save_svg == 1:
            param_all.update({'svg_folder': svg_dir})

        plotter = PlotOperator(**param_all)

        # # FIG 1: PRF ECC VS...
        # # --------------------

        # pRFecc
        old_main_fig = []
        f_pRFecc = []
        type_comp_list = ['Size','R2','Coverage','Baseline']
        
        for numData, type_comp in enumerate(type_comp_list):

            params_pRFecc = param_all
            params_pRFecc.update(
                       {    'x_range': (0, 15),
                            'x_label': 'Eccentricity (dva)',
                            'x_tick_steps': 5,
                            'x_source_label': 'ecc',
                            'draw_reg': False,
                            'h_hist_bins': 15,
                            'link_x': True})

            title = '{roi}: Eccentricity vs. {type_comp}'.format(roi = roi, type_comp = type_comp)
            params_pRFecc.update({'main_fig_title': title})

            if save_svg == 1:
                params_pRFecc.update({'svg_subfolder':'{roi}_{task}_{preproc}_pRFecc'.format(task = task, roi = roi, preproc = preproc)})

            if type_comp == 'Size':
                params_pRFecc.update(
                            {   'y_range': (0, 15),
                                'y_label': 'Size (dva)',
                                'y_source_label': 'sigma',
                                'y_tick_steps': 5,
                                'v_hist_bins': 15,
                                'draw_reg': True})
                if save_svg == 1:
                    params_pRFecc.update({'svg_filename':'{roi}_{task}_{preproc}_pRFecc_size'.format(task = task, roi = roi, preproc = preproc)})

            elif type_comp == 'R2':
                params_pRFecc.update(
                            {   'y_range': (0, 1),
                                'y_label': 'R2',
                                'y_source_label': 'rsq',
                                'y_tick_steps': 0.2,
                                'v_hist_bins': 20})
                if save_svg == 1:
                    params_pRFecc.update({'svg_filename':'{roi}_{task}_{preproc}_pRFecc_rsq'.format(task = task, roi = roi, preproc = preproc)})

            elif type_comp == 'Non-Linearity':
                params_pRFecc.update(
                            {   'y_range': (0, 1.5),
                                'y_label': 'Non-linearity',
                                'y_source_label': 'non_lin',
                                'y_tick_steps': 0.25,
                                'v_hist_bins': 30})
                if save_svg == 1:
                    params_pRFecc.update({'svg_filename':'{roi}_{task}_{preproc}_pRFecc_non_lin'.format(task = task, roi = roi, preproc = preproc)})


            elif type_comp == 'Coverage':
                params_pRFecc.update(
                            {   'y_range': (0, 1),
                                'y_label': 'pRF coverage (%)',
                                'y_source_label': 'cov',
                                'y_tick_steps': 0.2,
                                'v_hist_bins': 20})
                if save_svg == 1:
                    params_pRFecc.update({'svg_filename':'{roi}_{task}_{preproc}_pRFecc_cov'.format(task = task, roi= roi, preproc = preproc)})

            elif type_comp == 'Baseline':
                params_pRFecc.update(
                            {   'y_range': (-1, 1),
                                'y_label': 'Baseline',
                                'y_source_label': 'baseline',
                                'y_tick_steps': 0.5,
                                'v_hist_bins': 16})
                if save_svg == 1:
                    params_pRFecc.update({'svg_filename': '{roi}_{task}_{preproc}_pRFecc_baseline'.format(task = task,roi = roi, preproc = preproc)})

            out1, old_main_fig  = plotter.draw_figure(  parameters = params_pRFecc,
                                                        plot = 'ecc',
                                                        old_main_fig = old_main_fig)
            f_pRFecc.append(out1)

        all_fig1 = gridplot([ [f_pRFecc[0],f_pRFecc[1]],
                              [f_pRFecc[2],f_pRFecc[3]]],toolbar_location='right')


        exec('output_file_html = opj(html_dir,"{roi}_{task}_{preproc}_pRFecc.html")'.format(task = task, preproc = preproc, roi = roi))
        html_title = "Subject: {subject} | ROI: {roi} | Data: {task} {preproc} | Voxel num: {voxel_num} | Figures: pRF maps eccentricity vs.".format(
                                            subject = subject,roi = roi,task = task, preproc = preproc, voxel_num = voxel_num)
        output_file(output_file_html, title = html_title)
        save(all_fig1)
        

        # FIG 2: PRF MAP + PRF COV
        # ------------------------

        # pRFmap
        old_main_fig = []
        title = '{roi}: pRF map (n = {voxel_num})'.format(roi = roi, voxel_num = voxel_num)
        params_pRFmap = param_all

        params_pRFmap.update({   
                        'x_range': (-15, 15),
                        'y_range': (-15, 15),
                        'x_label': 'Horizontal coordinate (dva)',
                        'y_label': 'Vertical coordinate (dva)',
                        'x_source_label': 'x',
                        'y_source_label': 'y',
                        'x_tick_steps': 5,
                        'y_tick_steps': 5,
                        'v_hist_bins': 12,
                        'h_hist_bins': 12,
                        'main_fig_title': title})
        if save_svg == 1:
            params_pRFmap.update({'svg_filename': '{roi}_{task}_{preproc}_pRFmap'.format(task = task, preproc = preproc, roi= roi)})

        f_pRFmap, old_main_fig1 = plotter.draw_figure(  parameters = params_pRFmap, 
                                                        plot = 'map',
                                                        old_main_fig = old_main_fig)


        # pRF cov
        title = '{roi}: pRF density map'.format(roi = roi)
        params_pRFcov = param_all
        params_pRFcov.update({   
                        'x_range': (-15, 15), 
                        'y_range': (-15, 15),
                        'x_label': 'Horizontal coordinate (dva)',
                        'y_label': 'Vertical coordinate (dva)',
                        'x_tick_steps': 5,
                        'y_tick_steps': 5,
                        'smooth_factor': 15,
                        'cmap': 'viridis',
                        'cmap_steps': 10,
                        'col_offset': 0,
                        'vmin': 0,
                        'vmax': 1,
                        'cb_tick_steps': 0.2,
                        'cb_label': 'pRF coverage (norm.)',
                        'link_x': True,
                        'link_y': True})
        if save_svg == 1:
            params_pRFcov.update({'svg_filename': '{roi}_{task}_{preproc}_pRFcov'.format(task = task, roi = roi, preproc = preproc)})

        params_pRFcov.update({'main_fig_title':   title})

        f_pRFcov, old_main_fig1 = plotter.draw_figure( parameters = params_pRFcov, 
                                                       plot = 'cov',
                                                       old_main_fig = old_main_fig1)

        all_fig2 = gridplot([ [f_pRFmap,f_pRFcov]], toolbar_location = 'right')

        exec('output_file_html = opj(html_dir,"{roi}_{task}_{preproc}_pRFmap.html")'.format(task = task, preproc = preproc, roi = roi))
        html_title = "Subject: {subject} | ROI: {roi} | Data: {task} {preproc} | Voxel num: {voxel_num} | Figures: pRF maps parameters and density".format(
                                            subject = subject,roi = roi, task = task, preproc = preproc, voxel_num = voxel_num)
        output_file(output_file_html, title = html_title)
        save(all_fig2)
        

        # FIG 3: pRF laterality
        # ---------------------
        old_main_fig = []
        title = '{roi}: pRF laterality histogram'.format(roi = roi)
        params_pRFlat = param_all
        params_pRFlat.update(
                    {   'p_width': 500, 
                        'p_height': 500,
                        'dataMat': deriv_data,
                        'x_range': (-2.6, 2.6), 
                        'y_range': (-2.6, 2.6),
                        'vmin': 0,
                        'vmax': 0.2,
                        'weighted_data': True,
                        'main_fig_title': title,
                        'cmap': 'hsv',
                        'cmap_steps': 16,
                        'ang_bins': 36})
        if save_svg == 1:
            params_pRFlat.update({'svg_filename':'{roi}_{task}_{preproc}_pRFlat'.format(task = task, roi = roi, preproc = preproc)})

        params_pRFcov.update({'main_fig_title':   title})
        f_pRFlat, old_main_fig1 = plotter.draw_figure( parameters = params_pRFlat, 
                                                       plot = 'lat',
                                                       old_main_fig = old_main_fig)

        all_fig3 = gridplot([[f_pRFlat]],toolbar_location = 'right')
        exec('output_file_html = opj(html_dir,"{roi}_{task}_{preproc}_pRFlat.html")'.format(task = task, preproc = preproc, roi = roi))
        html_title = "Subject: {subject} | ROI: {roi} | Data: {task} {preproc} | Voxel num: {voxel_num} | Figures: pRF laterality histogram".format(
                                            subject = subject,roi = roi, task = task, voxel_num = voxel_num, preproc = preproc)
        output_file(output_file_html, title = html_title)
        save(all_fig3)

        # FIG 4: pRF time course
        # ----------------------

        step_r2 = [0,100/3.0,250/3.0,100]
        list_r2_level = ['High','Low']
        step_params = [0,100/3.0,200/3.0,100]
        list_params_level = ['Low','High']
        list_params = ['ecc','amp','size','cov']

        # pRF tc
        params_pRFtc = param_all
        
        if task == 'GazeCenterFS':
            trs = analysis_info['TRs'][0]
            stim_on = ([11,42],[53,70],[81,112],[123,140])
            stim_dir = (['left'],['down'],['right'],['up'])
        else:
            trs = analysis_info['TRs'][1]
            stim_on = ([11,28],[39,56],[67,84],[95,112])
            stim_dir = (['left'],['right'],['left'],['right'])
        
        params_pRFtc.update(
                    {   'p_width': 500, 
                        'p_height': 500,
                        'x_range_map': (-15,15),
                        'y_range_map': (-15,15),
                        'x_label_map': 'Horizontal coord. (dva)',
                        'y_label_map': 'Vertical coord. (dva)',
                        'x_tick_map': 5,
                        'y_tick_map': 5,
                        'x_range_tc': (0,trs*analysis_info['TR']),
                        'x_label_tc': 'Time (s)',
                        'y_label_tc': 'BOLD signal change (%)',
                        'x_tick_tc': 10,
                        'tr_dur': analysis_info['TR'],
                        'model_line_color': tuple([254,51,10]),
                        'model_fill_color': tuple([254,51,10])
                    })

        if save_svg == 1:
            params_pRFtc.update({'svg_subfolder': '{roi}_{task}_{preproc}_pRFtc'.format(task = task, preproc = preproc, roi = roi)})

        f_pRFtc = []

        # get index matrices
        prct_r2 = np.nanpercentile(a = deriv_data[:,rsq_idx],q = step_r2)
        idx_r2 = []

        for r2_step in np.arange(0,len(step_r2)-1,2):
            idx_r2.append(np.logical_and(deriv_data[:,rsq_idx]>=prct_r2[r2_step],deriv_data[:,rsq_idx]<=prct_r2[r2_step+1]))

        # get voxel number to draw
        for param in list_params:

            exec('prct_{param} = np.nanpercentile(a = deriv_data[:,{param}_idx],q = step_params)'.format(param = param))
            exec('idx_{param} = []'.format(param = param))

            for param_step in np.arange(0,len(step_params)-1,2):
                exec('idx_{param}.append(np.logical_and(deriv_data[:,{param}_idx]>=prct_{param}[param_step],deriv_data[:,{param}_idx]<=prct_{param}[param_step+1]))'.format(param = param))


            exec('num_{param} = []'.format(param = param))

            for r2_step in np.arange(0,2,1):

                for param_step in np.arange(0,2,1):

                    exec('mat = np.where(np.logical_and(idx_r2[r2_step],idx_{param}[param_step]))'.format(param = param))

                    if mat[0].size == 0:
                        exec('num_{param}.append(-1)'.format(param = param))
                    else:
                        exec('num_{param}.append(mat[0][np.random.choice(len(mat[0]))])'.format(param = param))


        for param in list_params:
            exec('num_voxel = num_{param}'.format(param = param))

            for r2_level in list_r2_level:
                if r2_level == 'Low':
                    num_voxel2draw = num_voxel[0:2]
                elif r2_level == 'High':
                    num_voxel2draw = num_voxel[2:4]

                params_pRFtc.update(
                                {   'params': param,
                                    'r2_level': r2_level,
                                    'deriv_mat': deriv_data,
                                    'tc_mat': tc_data,
                                    'tc_model_mat': tc_model_data,
                                    'num_voxel': num_voxel2draw,
                                    'coord_mat':coord_data,
                                    'stim_on': stim_on,
                                    'stim_dir': stim_dir,
                                    'title': '{roi}'.format(roi = roi)
                                })
                if save_svg == 1:
                    params_pRFtc.update({'svg_filename':'{roi}_{task}_{preproc}_pRFtc_rsq_{r2_level}_{param}'.format(task = task, preproc = preproc, roi = roi,r2_level = r2_level, param = param)})

                out4,main_fig4  = plotter.draw_figure(  parameters = params_pRFtc,
                                                        plot = 'tc')



                f_pRFtc.append(out4)

        all_fig4 = gridplot([   [f_pRFtc[0],f_pRFtc[1]],
                                [f_pRFtc[2],f_pRFtc[3]],
                                [f_pRFtc[4],f_pRFtc[5]],
                                [f_pRFtc[6],f_pRFtc[7]]],toolbar_location = None)

        exec('output_file_html = opj(html_dir,"{roi}_{task}_{preproc}_pRFtc.html")'.format(task = task, preproc = preproc, roi = roi))
        html_title = "Subject: {subject} | ROI: {roi} | Data: {task} {preproc} | Voxel num: {voxel_num} | Figures: pRF time course".format(
                                            subject = subject,roi = roi, task = task, preproc = preproc, voxel_num = voxel_num)
        output_file(output_file_html, title = html_title)
        save(all_fig4)

    else:
        print("drawing {roi}_{task}_{preproc} figures not possible: n = {voxel_num}".format(roi = roi, voxel_num = voxel_num, task = task, preproc = preproc))