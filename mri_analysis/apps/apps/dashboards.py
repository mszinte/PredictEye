def plotly_template(template_specs):

    import plotly.graph_objects as go

    # Layout
    fig_template=go.layout.Template()
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
                                    ))

    # Annotations
    fig_template.layout.annotationdefaults = go.layout.Annotation(
                                    font_color=template_specs['axes_color'],
                                    font_family=template_specs['font'],
                                    font_size=template_specs['title_font_size'])

    return fig_template
    

def tc_plot(df_plot,numplot):

    import plotly.graph_objects as go
    import numpy as np


    # general figure settings
    template_specs = dict(  axes_color="rgba(0, 0, 0, 1)",          # figure axes color
                            axes_width=2,                           # figureaxes line width
                            axes_font_size=15,                      # font size of axes
                            bg_col="rgba(255, 255, 255, 1)",        # figure background color
                            font='Helvetica',                       # general font used
                            title_font_size=18,                     # font size of titles
                            plot_width=1.5,                         # plot line width
                            )

    fig_template = plotly_template(template_specs)

    fig_height, fig_width = 250,1000
    rows, cols = 1, 2

    x_label_tc, y_label_tc = '# TR', 'z-score'
    x_range_tc, y_range_tc = [0,208], [-3,3]
    x_tickvals_tc = np.linspace(x_range_tc[0],x_range_tc[1],14)
    y_tickvals_tc = np.linspace(y_range_tc[0],y_range_tc[1],5)
    x_ticktexts_tc = ['{:g}'.format(x) for x in x_tickvals_tc]
    y_ticktexts_tc = ['{:g}'.format(x) for x in y_tickvals_tc]

    x_label_map, y_label_map = 'Hor. coord. (dva)', 'Ver. coord. (dva)',
    y_range_map, x_range_map = [-15,15], [-15,15]
    x_tickvals_map = np.linspace(x_range_map[0],x_range_map[1],5)
    y_tickvals_map = np.linspace(y_range_map[0],y_range_map[1],5)
    x_ticktexts_map = ['{:g}'.format(x) for x in x_tickvals_map]
    y_ticktexts_map = ['{:g}'.format(x) for x in y_tickvals_map]


    # subplot settings
    row_heights = [4]
    column_widths = [4,1]

    sb_specs = [[{},{}]]
    fig = make_subplots(rows=rows, cols=cols, specs=sb_specs, print_grid=False, vertical_spacing=0.1, horizontal_spacing=0.5/5,
                        column_widths=column_widths, row_heights=row_heights, shared_yaxes=False)

    # draw data timecourse
    fig.append_trace(go.Scatter(y=df_plot.signal_tc.values[numplot],
                                mode='markers', name='data',showlegend=False,
                                marker_symbol='circle', marker_size=3, marker_color='black',
                                marker_line_color='black',marker_line_width = 0.5),row=1, col=1)

    # draw model timecourse
    fig.append_trace(go.Scatter(y=df_plot.model_tc.values[numplot],
                                mode='lines', name='model',showlegend=False,
                                line_color='red'),row=1, col=1)

    # draw model map
    x_model, y_model = df_plot.x.values[numplot], df_plot.y.values[numplot]
    size_model = df_plot['size'].values[numplot]
    fig.add_shape(type="circle", x0=x_model-size_model/2, y0=y_model-size_model/2, x1=x_model+size_model/2, y1=y_model+size_model/2, fillcolor= 'red', row=1, col=2) 

    # add annotations
    fig.add_annotation( xref="paper", yref="paper", x=0.01, y=1, showarrow=False, font_size=12,
                        text="coord: [{xcoord:0.0f},{ycoord:0.0f},{zcoord:0.0f}]".format(  xcoord=df_plot.voxel_coords.values[numplot][0],
                                                                            ycoord=df_plot.voxel_coords.values[numplot][1],
                                                                            zcoord=df_plot.voxel_coords.values[numplot][2],))
    fig.add_annotation( xref="paper", yref="paper", x=0.01, y=0.9, showarrow=False, font_size=12,
                        text="R\u00b2: {:1.2f}".format(df_plot.rsq.values[numplot]))


    # figure layout
    fig.layout.update(  # figure settings
                        template=fig_template, width=fig_width, height=fig_height, margin_l=70, margin_r=20, margin_t=20, margin_b=70,
                        
                        # timecourse
                        yaxis_visible=True, yaxis1_linewidth=template_specs['axes_width'], yaxis1_title_text=y_label_tc, 
                        yaxis1_range=y_range_tc, yaxis1_ticklen=8, yaxis1_tickvals=y_tickvals_tc, yaxis1_ticktext=y_ticktexts_tc,
                        xaxis1_visible=True, xaxis1_linewidth=template_specs['axes_width'], xaxis1_title_text=x_label_tc, 
                        xaxis1_range=x_range_tc, xaxis1_ticklen=8, xaxis1_tickvals=x_tickvals_tc, xaxis1_ticktext=x_ticktexts_tc,

                        # map
                        yaxis2_visible=True, yaxis2_linewidth=template_specs['axes_width'], yaxis2_title_text=y_label_map, 
                        yaxis2_range=y_range_map, yaxis2_ticklen=8, yaxis2_ticktext=y_ticktexts_map,
                        yaxis2_zeroline=True, yaxis2_zerolinecolor='rgba(0,0,0,0.5)',
                        xaxis2_visible=True, xaxis2_linewidth=template_specs['axes_width'], xaxis2_title_text=x_label_map, 
                        xaxis2_range=x_range_map, xaxis2_ticklen=8, xaxis2_tickvals=x_tickvals_map, xaxis2_ticktext=x_ticktexts_map,
                        xaxis2_zeroline=True, xaxis2_zerolinecolor='rgba(0,0,0,0.5)',
                        )

    return fig


def plot_motor_design(sub_task, seq_num, pmf_ecc, pmf_angle, pmf_size):

    import numpy as np
    import scipy.io
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from .utils import compute_pmf

    # analysis settings
    trs_break = 16                                                  # trs during break period
    trs_eye_mov = 32                                                # trs during eye movement
    ppd = 52                                                        # pixel per degrees
    amp_eyemov = np.linspace(2.5,10,4)*ppd                          # smooth pursuit and saccade amplitude
    pix_ratio = 0.125                                               # ratio of pixel motor design for later fit
    TRs = 208                                                       # total number of TR

    # load and compute data
    vd_file = scipy.io.loadmat("apps/data/vd/pMF{}_vd_seq{}.mat".format(sub_task, seq_num))
    stim = vd_file['stim']                                          # load design
    screen_width, screen_height = stim.shape[0],stim.shape[1]       # screen pixel size
    tc_norm, pmf_norm = compute_pmf(sub_task, seq_num, pmf_ecc,\
                                           pmf_angle,pmf_size)     # compute pmf

    # figure settings
    template_specs = dict(  axes_color="rgba(0, 0, 0, 1)",          # figure axes color
                            axes_width=2,                           # figureaxes line width
                            axes_font_size=15,                      # font size of axes
                            bg_col="rgba(255, 255, 255, 1)",        # figure background color
                            font='Helvetica',                       # general font used
                            title_font_size=18,                     # font size of titles
                            plot_width=1.5,                         # plot line width
                            )
    fig_template = plotly_template(template_specs)                  # general figure template
    fig_height, fig_width = 500,1000                                # figure heigth and width
    rows, cols = 2, 4                                               # number of rows and columns
    row_heights = [1,1]                                             # row heigth                                      
    column_widths = [1,1,1,1]                                       # column width
    sb_specs = [[{},{},{},{}],                                      # subplot specs
                [{'colspan':3},None,None,{}]]
    
    # axis settings
    x_label_map, y_label_map = 'Hor. coord. (dva)', 'Ver. coord. (dva)',
    x_range_map, y_range_map = [0,screen_width], [0,screen_height]
    x_tickvals_map, y_tickvals_map = np.linspace(0,screen_width-1,5), np.linspace(0,screen_height-1,5)
    x_ticktexts_map = ['{:g}'.format(x) for x in np.linspace(-15,15,5)]
    y_ticktexts_map = ['{:g}'.format(x) for x in np.linspace(15,-15,5)]

    x_label_tc, y_label_tc = '# TR', 'Signal (a.u.)'
    x_range_tc, y_range_tc = [0,TRs], [-0.5,1]
    x_tickvals_tc = np.linspace(x_range_tc[0],x_range_tc[1],14)
    y_tickvals_tc = np.linspace(y_range_tc[0],y_range_tc[1],4)
    x_ticktexts_tc = ['{:g}'.format(x) for x in x_tickvals_tc]
    y_ticktexts_tc = ['{:g}'.format(x) for x in y_tickvals_tc]

    # create subplot
    fig = make_subplots(rows=rows,
                        cols=cols,
                        specs=sb_specs,
                        print_grid=False,
                        vertical_spacing=0.2,
                        horizontal_spacing=0.1,
                        shared_yaxes=False)

    # motor design subplots
    for seq_num in [1,2,3,4]:
        seq_stim = np.sum(stim[:,:,seq_num*trs_break+(seq_num-1)*trs_eye_mov:seq_num*trs_break+seq_num*trs_eye_mov], axis=2)
        fig.add_trace(  go.Heatmap( z=seq_stim,
                                    colorscale='viridis',
                                    showscale = False),
                        row=1, col=seq_num)

        for rad_num in [0,1,2,3]:
            rad_circle = amp_eyemov[rad_num]*pix_ratio
            fig.add_shape(  type="circle",
                            x0=screen_width/2-rad_circle, y0=screen_height/2-rad_circle,
                            x1=screen_width/2+rad_circle, y1=screen_height/2+rad_circle,
                            line_color='white',
                            line_dash='dot',
                            line_width=1,
                            row = 1, col = seq_num)

    # model time course and map subplots
    fig.add_trace(  go.Scatter( y=tc_norm[0],
                                mode='lines', 
                                name='model',
                                showlegend=False,
                                line_color='black'),
                    row=2, col=1)

    fig.add_trace(  go.Heatmap( z=pmf_norm,
                                colorscale='viridis',
                                showscale=False),
                    row=2, col=4)

    for rad_num in [0,1,2,3]:
        rad_circle = amp_eyemov[rad_num]*pix_ratio
        fig.add_shape(  type="circle",
                        x0=screen_width/2-rad_circle, y0=screen_height/2-rad_circle,
                        x1=screen_width/2+rad_circle, y1=screen_height/2+rad_circle,
                        line_color='white',
                        line_dash='dot',
                        line_width=1,
                        row = 2, col = seq_num)

    # figure layout
    fig.layout.update(  # figure settings
                        template=fig_template, width=fig_width, height=fig_height, margin_l=70, margin_r=20, margin_t=20, margin_b=70,

                        xaxis1_visible=True, xaxis1_linewidth=template_specs['axes_width'], xaxis1_title_text=x_label_map, 
                        xaxis1_range=x_range_map, xaxis1_ticklen=8, xaxis1_ticktext=x_ticktexts_map, xaxis1_tickvals=x_tickvals_map,
                        yaxis1_visible=True, yaxis1_linewidth=template_specs['axes_width'], yaxis1_title_text=y_label_map, 
                        yaxis1_range=y_range_map, yaxis1_ticklen=8, yaxis1_ticktext=y_ticktexts_map, yaxis1_tickvals=y_tickvals_map,
                        yaxis1_autorange = 'reversed',
                        
                        xaxis2_visible=True, xaxis2_linewidth=template_specs['axes_width'], xaxis2_title_text=x_label_map, 
                        xaxis2_range=x_range_map, xaxis2_ticklen=8, xaxis2_ticktext=x_ticktexts_map, xaxis2_tickvals=x_tickvals_map,
                        yaxis2_visible=True, yaxis2_linewidth=template_specs['axes_width'], yaxis2_title_text=y_label_map, 
                        yaxis2_range=y_range_map, yaxis2_ticklen=8, yaxis2_ticktext=y_ticktexts_map, yaxis2_tickvals=y_tickvals_map,
                        yaxis2_autorange = 'reversed',

                        xaxis3_visible=True, xaxis3_linewidth=template_specs['axes_width'], xaxis3_title_text=x_label_map, 
                        xaxis3_range=x_range_map, xaxis3_ticklen=8, xaxis3_ticktext=x_ticktexts_map, xaxis3_tickvals=x_tickvals_map,
                        yaxis3_visible=True, yaxis3_linewidth=template_specs['axes_width'], yaxis3_title_text=y_label_map, 
                        yaxis3_range=y_range_map, yaxis3_ticklen=8, yaxis3_ticktext=y_ticktexts_map, yaxis3_tickvals=y_tickvals_map,
                        yaxis3_autorange = 'reversed',

                        xaxis4_visible=True, xaxis4_linewidth=template_specs['axes_width'], xaxis4_title_text=x_label_map, 
                        xaxis4_range=x_range_map, xaxis4_ticklen=8, xaxis4_ticktext=x_ticktexts_map, xaxis4_tickvals=x_tickvals_map,
                        yaxis4_visible=True, yaxis4_linewidth=template_specs['axes_width'], yaxis4_title_text=y_label_map, 
                        yaxis4_range=y_range_map, yaxis4_ticklen=8, yaxis4_ticktext=y_ticktexts_map, yaxis4_tickvals=y_tickvals_map,
                        yaxis4_autorange = 'reversed',

                        yaxis5_visible=True, yaxis5_linewidth=template_specs['axes_width'], yaxis5_title_text=y_label_tc, 
                        yaxis5_range=y_range_tc, yaxis5_ticklen=8, yaxis5_tickvals=y_tickvals_tc, yaxis5_ticktext=y_ticktexts_tc,
                        xaxis5_visible=True, xaxis5_linewidth=template_specs['axes_width'], xaxis5_title_text=x_label_tc, 
                        xaxis5_range=x_range_tc, xaxis5_ticklen=8, xaxis5_tickvals=x_tickvals_tc, xaxis5_ticktext=x_ticktexts_tc,

                        xaxis6_visible=True, xaxis6_linewidth=template_specs['axes_width'], xaxis6_title_text=x_label_map, 
                        xaxis6_range=x_range_map, xaxis6_ticklen=8, xaxis6_ticktext=x_ticktexts_map, xaxis6_tickvals=x_tickvals_map,
                        yaxis6_visible=True, yaxis6_linewidth=template_specs['axes_width'], yaxis6_title_text=y_label_map, 
                        yaxis6_range=y_range_map, yaxis6_ticklen=8, yaxis6_ticktext=y_ticktexts_map, yaxis6_tickvals=y_tickvals_map,
                        yaxis6_autorange = 'reversed',
                        
                        )

    return fig
