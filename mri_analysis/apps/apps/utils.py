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


    import numpy as np

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

def save_motor_design(sub_tasks,eyemov_sd):

    import numpy as np
    from PIL import Image 
    import itertools
    import scipy.io
    
    # compute parameters
    trs_break = 16                                                  # trs during break period
    trs_eye_mov = 32                                                # trs during eye movement period
    ppd = 52                                                        # nb of pixels per degrees
    TRs = 208                                                       # total number of TR
    screen_width_px, screen_height_px = 1080,1080                   # screen width and height in pixel
    eyemove_height_dva = 30                                         # eye movement are height in dva
    pix_ratio = 0.125                                               # ratio of pixel motor design for later fit
    ratio_out = eyemove_height_dva/(screen_height_px/ppd)           # ratio to compute of out of screen pixel size eye movement can be made
    screen = [screen_width_px,screen_height_px]                     # screen resolution in pixels (use height of pRF)
    screen = [int(screen[0]*ratio_out),int(screen[1]*ratio_out)]    # screen recomputed size
    center = [screen[0]/2,screen[1]/2]                              # screen center 
    dir_sp = np.deg2rad(np.arange(0,360,22.5))                      # smooth pursuit directions in radian
    dir_sac = np.deg2rad(np.arange(0,360,22.5)+180)                 # saccade directions in radian
    sp_amp = np.linspace(2.5,10,4)*ppd                              # smooth pursuit amplitude/speed
    sac_amp = np.linspace(2.5,10,4)*ppd                             # saccade amplitude

    sp_radial_sd = eyemov_sd[0]
    sp_tangential_sd = eyemov_sd[1]
    sac_radial_sd = eyemov_sd[2]
    sac_tangential_sd = eyemov_sd[3]

    sigma_sp  =[[sp_radial_sd[0]*ppd, sp_tangential_sd[0]*ppd],     # smooth pursuit area sd for first amplitude
                [sp_radial_sd[1]*ppd, sp_tangential_sd[1]*ppd],     # smooth pursuit area sd for second amplitude
                [sp_radial_sd[2]*ppd, sp_tangential_sd[2]*ppd],     # smooth pursuit area sd for third amplitude
                [sp_radial_sd[3]*ppd, sp_tangential_sd[3]*ppd]]     # smooth pursuit area sd for fourth amplitude

    sigma_sac =[[sac_radial_sd[0]*ppd, sac_tangential_sd[0]*ppd],   # saccade area sd for first amplitude
                [sac_radial_sd[1]*ppd, sac_tangential_sd[1]*ppd],   # saccade area sd for second amplitude
                [sac_radial_sd[2]*ppd, sac_tangential_sd[2]*ppd],   # saccade area sd for third amplitude
                [sac_radial_sd[3]*ppd, sac_tangential_sd[3]*ppd]]   # saccade area sd for fourth amplitude

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

            mat_file_name = "apps/data/vd/pMF{}_vd_seq{}.mat".format(sub_task, seq_num)
            scipy.io.savemat(file_name=mat_file_name, mdict=mat_dict, do_compression=True)
            print("subtask: {}, permutation : {}".format(sub_task,seq_num))
            seq_num += 1
        
    return None

def compute_pmf(sub_task, seq_num, ecc, angle, size):

    # general import
    import numpy as np
    import scipy.io

    # model imports
    # -------------
    from prfpy.stimulus import PRFStimulus2D
    from prfpy.model import Iso2DGaussianModel
    from prfpy.fit import Iso2DGaussianFitter

    ppd = 52                                                        # nb of pixels per degrees
    eyemove_height_dva = 30                                         # eye movement are height in dva
    screen_width_px,screen_height_px = 1080,1080                    # screen size
    ratio_out = eyemove_height_dva/(screen_height_px/ppd)           # ratio to compute of out of screen pixel size eye movement can be made
    screen_height_cm = 43.5 * ratio_out
    screen_width_cm = 43.5 * ratio_out
    screen_distance_cm = 120
    TR = 1.2
    TRs = 208
    vd_file = scipy.io.loadmat("apps/data/vd/pMF{}_vd_seq{}.mat".format(sub_task, seq_num))

    # determine model
    vd = vd_file['stim']
    stimulus = PRFStimulus2D(   screen_size_cm=screen_width_cm,
                                screen_distance_cm=screen_distance_cm,
                                design_matrix=vd,
                                TR=TR)
    gauss_model = Iso2DGaussianModel(stimulus=stimulus, normalize_RFs = True)

    # model parameters
    angle_rad = np.deg2rad(angle)
    mu_x = np.cos(angle_rad)*ecc
    mu_y = np.sin(angle_rad)*ecc
    beta = 1
    baseline = 0

    # define model time course
    tc_raw = gauss_model.return_prediction( mu_x=np.array(mu_x), 
                                            mu_y=np.array(mu_y),
                                            size=np.array(size), 
                                            beta=np.array(1), 
                                            baseline=np.array(baseline))
    tc_norm = ((tc_raw - np.min(tc_raw)) / (np.max(tc_raw) - np.min(tc_raw))) - ((baseline - np.min(tc_raw)) / (np.max(tc_raw) - np.min(tc_raw))) 

    # define model motor field
    gauss_fitter = Iso2DGaussianFitter(data=tc_norm, model=gauss_model)
    gauss_fitter.grid_fit(ecc_grid=ecc, polar_grid = angle_rad, size_grid=size)
    gauss_model.create_rfs()
    pmf = gauss_model.grid_rfs[0,:,:]
    pmf_norm = ((pmf - np.min(pmf)) / (np.max(pmf) - np.min(pmf)))*255

    return (tc_norm, pmf_norm,)
