def weighted_regression(x_reg,y_reg,weight_reg):
    """
    Function to compute regression parameter weighted by a matrix (e.g. r2 value).

    Parameters
    ----------
    x_reg : array (1D)
        x values to regress
    y_reg : array
        y values to regress
    weight_reg : array (1D) 
        weight values (0 to 1) for weighted regression

    Returns
    -------
    coef_reg : array
        regression coefficient
    intercept_reg : str
        regression intercept
    """

    from sklearn import linear_model
    import numpy as np
    
    regr = linear_model.LinearRegression()
    
    def m(x, w):
        return np.sum(x * w) / np.sum(w)

    def cov(x, y, w):
        # see https://www2.microstrategy.com/producthelp/archive/10.8/FunctionsRef/Content/FuncRef/WeightedCov__weighted_covariance_.htm
        return np.sum(w * (x - m(x, w)) * (y - m(y, w))) / np.sum(w)

    def weighted_corr(x, y, w):
        # see https://www2.microstrategy.com/producthelp/10.4/FunctionsRef/Content/FuncRef/WeightedCorr__weighted_correlation_.htm
        return cov(x, y, w) / np.sqrt(cov(x, x, w) * cov(y, y, w))

    x_reg_nan = x_reg[(~np.isnan(x_reg) & ~np.isnan(y_reg))]
    y_reg_nan = y_reg[(~np.isnan(x_reg) & ~np.isnan(y_reg))]
    weight_reg_nan = weight_reg[~np.isnan(weight_reg)]

    regr.fit(x_reg_nan.reshape(-1, 1), y_reg_nan.reshape(-1, 1),weight_reg_nan)
    coef_reg, intercept_reg = regr.coef_, regr.intercept_

    return coef_reg, intercept_reg

def rgb2rgba(input_col,alpha_val):
    """
    Function to add an alpha value to color input in plotly

    Parameters
    ----------
    input_col : str
        color value (e.g. 'rgb(200,200,200)')
    alapha_val : float
        transparency valu (0 > 1.0)
    
    Returns
    -------
    rgba_col : str 
        color value in rgba (e.g. 'rgba(200,200,200,0.5)')
    """

    rgba_col = "rgba{}, {})".format(input_col[3:-1],alpha_val)
    return rgba_col

def adjust_lightness(input_rgb, amount=0.5):
    """
    Function to change lightness of a specific rgb color

    Parameters
    ----------
    input_rgb : str
        color value (e.g. 'rgb(200,200,200)')
    amount : float
        amount of lightness change (-1.0 to 1.0)
    
    Returns
    -------
    output_col : str
        color value in rgb (e.g. 'rgba(200,200,200)')
    """

    import colorsys
    import matplotlib.colors as mc
    import numpy as np
    c = np.array(list(map(float, input_rgb[4:-1].split(','))))/255
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    r,g,b=colorsys.hls_to_rgb(c[0], max(0, min(1,  amount* c[1])), c[2])
    r,g,b=int(np.round(r*255,0)),int(np.round(g*255,0)),int(np.round(b*255,0))

    output_col = "rgb({},{},{})".format(r,g,b)
    return output_col

def plotly_template(template_specs):
    """
    Define the template for plotly

    Parameters
    ----------
    template_specs : dict
        dictionary contain specific figure settings
    
    Returns
    -------
    fig_template : plotly.graph_objs.layout._template.Template
        Template for plotly figure
    """
    import plotly.graph_objects as go
    fig_template=go.layout.Template()

    # Violin plots
    fig_template.data.violin = [go.Violin(
                                    box_visible=False,
                                    points=False,
                                    opacity=1,
                                    line_color= "rgba(0, 0, 0, 1)",
                                    line_width=template_specs['plot_width'],
                                    width=0.8,
                                    marker_symbol='x',
                                    marker_opacity=0.5,
                                    hoveron='violins',
                                    meanline_visible=True,
                                    meanline_color="rgba(0, 0, 0, 1)",
                                    meanline_width=template_specs['plot_width'],
                                    showlegend=False,
                                    )]

    fig_template.data.barpolar = [go.Barpolar(
                                    marker_line_color="rgba(0,0,0,1)",
                                    marker_line_width=template_specs['plot_width'], 
                                    showlegend=False, 
                                    thetaunit = 'radians'
                                    )]

    # Pie plots
    fig_template.data.pie = [go.Pie(showlegend=False,
                                    textposition=["inside","none"],
                                    marker_line_color=['rgba(0,0,0,1)','rgba(255,255,255,0)'],
                                    marker_line_width=[template_specs['plot_width'],0],
                                    rotation=0,
                                    direction="clockwise",
                                    hole=0.4,
                                    sort=False,
                                    )]

    # Layout
    fig_template.layout = (go.Layout(# general
                                    font_family=template_specs['font'],
                                    font_size=template_specs['axes_font_size'],
                                    plot_bgcolor=template_specs['bg_col'],

                                    # x axis
                                    xaxis_visible=True,
                                    xaxis_linewidth=template_specs['axes_width'],
                                    xaxis_color= template_specs['axes_color'],
                                    xaxis_showgrid=False,
                                    xaxis_ticks="outside",
                                    xaxis_ticklen=0,
                                    xaxis_tickwidth = template_specs['axes_width'],
                                    xaxis_title_font_family=template_specs['font'],
                                    xaxis_title_font_size=template_specs['title_font_size'],
                                    xaxis_tickfont_family=template_specs['font'],
                                    xaxis_tickfont_size=template_specs['axes_font_size'],
                                    xaxis_zeroline=False,
                                    xaxis_zerolinecolor=template_specs['axes_color'],
                                    xaxis_zerolinewidth=template_specs['axes_width'],
                                    xaxis_range=[0,1],
                                    xaxis_hoverformat = '.1f',
                                    
                                    # y axis
                                    yaxis_visible=False,
                                    yaxis_linewidth=0,
                                    yaxis_color= template_specs['axes_color'],
                                    yaxis_showgrid=False,
                                    yaxis_ticks="outside",
                                    yaxis_ticklen=0,
                                    yaxis_tickwidth = template_specs['axes_width'],
                                    yaxis_tickfont_family=template_specs['font'],
                                    yaxis_tickfont_size=template_specs['axes_font_size'],
                                    yaxis_title_font_family=template_specs['font'],
                                    yaxis_title_font_size=template_specs['title_font_size'],
                                    yaxis_zeroline=False,
                                    yaxis_zerolinecolor=template_specs['axes_color'],
                                    yaxis_zerolinewidth=template_specs['axes_width'],
                                    yaxis_hoverformat = '.1f',

                                    # bar polar
                                    polar_radialaxis_visible = False,
                                    polar_radialaxis_showticklabels=False,
                                    polar_radialaxis_ticks='',
                                    polar_angularaxis_visible = False,
                                    polar_angularaxis_showticklabels = False,
                                    polar_angularaxis_ticks = ''
                                    ))

    # Annotations
    fig_template.layout.annotationdefaults = go.layout.Annotation(
                                    font_color=template_specs['axes_color'],
                                    font_family=template_specs['font'],
                                    font_size=template_specs['title_font_size'])

    return fig_template


def create_dataframe(subject,task,preproc,analysis_info):
    """
    Function to create compressed dataframe for dash app

    Parameters
    ----------
    subject : str
        subject name (e.g. 'sub-001')
    task : str
        data task (e.g. 'GazeCenterFS')
    preproc : str
        pre-processing of data ('fmriprep_dca')
    analysis_info : dict
        dictionary with experiment analysis information

    Returns
    -------
    df_name : str
        directory and filename of the dataframe
    """

    # General imports
    import os
    import numpy as np
    import h5py
    import pandas as pd

    # DATA
    # ----
    base_dir = analysis_info['base_dir']
    h5_dir = "{base_dir}/pp_data/{subject}/gauss/h5".format(base_dir = base_dir, subject = subject)
    pandas_dir = "{base_dir}/pp_data/{subject}/gauss/pandas".format(base_dir = base_dir, subject = subject)

    # load deriv data
    rsq_idx, ecc_idx, polar_real_idx, polar_imag_idx , size_idx, \
        amp_idx, baseline_idx, cov_idx, x_idx, y_idx, hemi_idx = 0,1,2,3,4,5,6,7,8,9,10
    rsq_dict, ecc_dict, polar_real_dict, polar_imag_dict, size_dict, x_dict, y_dict, hemi_dict = {}, {}, {}, {}, {}, {}, {}, {}
    ecc_sample_dict, size_sample_dict = {}, {}

    # create raw dataframe
    df_raw = pd.DataFrame()
    for roi in analysis_info['rois']:
        
        h5_file = h5py.File("{h5_dir}/{roi}_{task}_{preproc}.h5".format(h5_dir = h5_dir, roi = roi, task = task, preproc = preproc),'r')
        deriv_data = h5_file['{folder_alias}/derivatives'.format(folder_alias = 'pRF')]
        df_roi = pd.DataFrame(deriv_data,columns = ['rsq','ecc','polar_real','polar_imag','size','amp','baseline','cov','x','y','hemi'])
        df_roi['roi']=[roi for x in range(df_roi.shape[0])]
        df_roi['subject']=[subject for x in range(df_roi.shape[0])]
        df_roi['task']=[task for x in range(df_roi.shape[0])]
        df_roi['preproc']=[preproc for x in range(df_roi.shape[0])]
        df_raw = pd.concat([df_raw, df_roi],ignore_index=True, axis = 0)

    # save dataframe
    try: os.makedirs(pandas_dir)
    except: pass

    df_name = '{pandas_dir}/{subject}_{task}_{preproc}.gz'.format(pandas_dir=pandas_dir, subject=subject, task=task, preproc=preproc)
    df_raw.to_csv(df_name,compression='gzip', float_format='%.4f')

    return df_name