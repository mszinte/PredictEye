import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
from .utils import *

def prf_dashboard(df, analysis_info):

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

    fig_height, fig_width = 900,1200
    rois_colors = px.colors.qualitative.Prism
    rois_colors.append('rgb(180, 180, 180)')
    rois = analysis_info['rois']
    rows, cols = 4, 12

    y_label_trace, x_label_trace, trace_range = 'Size (dva)', 'Eccentricity (dva)', [0,12], 
    trace_tickvals = np.linspace(trace_range[0],trace_range[1],4)
    trace_ticktexts = ['{:g}'.format(x) for x in trace_tickvals]
    line_x = np.linspace(trace_range[0], trace_range[1], 60)
    bins = 12
    bin_angle = 2*np.pi/bins
    barpolar_hovertemplate = "Angle: %{text:.0f}°<br>Prop: %{r:.0f}%<extra></extra>"
    barpolar_range=[0,30]

    # subplot settings
    column_widths = [1,1,1,1,1,1,1,1,1,1,1,1,]
    row_heights = [4,1,1,4]
    sb_specs = [[{},{},{},{},{},{},{},{},{},{},{},{}],
                [{'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'},
                {'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'},{'type':'barpolar'}],
                [{'type':'domain'},{'type':'domain'},{'type':'domain'},{'type':'domain'},{'type':'domain'},{'type':'domain'},
                {'type':'domain'},{'type':'domain'},{'type':'domain'},{'type':'domain'},{'type':'domain'},{'type':'domain'}],
                [{'colspan':4},None,None,None,{'colspan':4},None,None,None,{'colspan':4},None,None,None]]

    fig = make_subplots(rows=rows, cols=cols, specs=sb_specs, print_grid=False, vertical_spacing=0.04, horizontal_spacing=0.02,
                        column_widths=column_widths, row_heights=row_heights, shared_yaxes=True)

    cols_violin, rows_violin        = [1,2,3,4,5,6,7,8,9,10,11,12], [1,1,1,1,1,1,1,1,1,1,1,1]
    cols_barpolar, rows_barpolar    = [1,2,3,4,5,6,7,8,9,10,11,12], [2,2,2,2,2,2,2,2,2,2,2,2]
    cols_pie, rows_pie              = [1,2,3,4,5,6,7,8,9,10,11,12], [3,3,3,3,3,3,3,3,3,3,3,3]
    cols_trace, rows_trace          = [1,1,1,1,5,5,5,5,9, 9, 9, 9], [4,4,4,4,4,4,4,4,4,4,4,4]

    # DRAWING
    # -------
    for num,(roi,roi_color) in enumerate(zip(rois,rois_colors)):
        
        # r2 violin plots
        fig.append_trace(go.Violin( y= df[df.roi==roi].rsq, name=roi, span=[0, 1], orientation= "v", spanmode='manual', fillcolor=roi_color), 
                                    row=rows_violin[num], col=cols_violin[num])

        # polar angle
        if df[df['roi']==roi].shape[0] >= 1:
            pol_angles = np.angle(df[df.roi==roi].polar_real + 1j * df[df.roi==roi].polar_imag)
            hist, bin_edges = np.histogram(a=pol_angles, range=(-np.pi,np.pi), bins = bins, weights=df[df.roi==roi].rsq)
            fig.append_trace(go.Barpolar(r=(hist/np.nansum(hist))*100, theta=bin_edges, width=np.ones_like(hist)*bin_angle, 
                                        text=np.rad2deg(bin_edges),hovertemplate=barpolar_hovertemplate, marker_color=roi_color),
                                        row=rows_barpolar[num], col=cols_barpolar[num])
        
        # contra-laterality ratio
        rh_ratio = np.nan
        if df[(df.hemi==2) & (df.roi==roi)].shape[0]!=0:
            rh_ratio = df[(df.hemi==2) & (df.x < 0) & (df.roi==roi)].rsq.sum() / df[(df.hemi==2) & (df.roi==roi)].rsq.sum()
        lh_ratio = np.nan
        if df[(df.hemi==1) & (df.roi==roi)].shape[0]!=0:
            lh_ratio = df[(df.hemi==1) & (df.x > 0) & (df.roi==roi)].rsq.sum() / df[(df.hemi==1) & (df.roi==roi)].rsq.sum()
        
        cl_ratio = np.nanmean([rh_ratio,lh_ratio])
        fig.append_trace(go.Pie(labels=["Contra-lateral","Ipsi-lateral"],hoverinfo='label+percent', values=[cl_ratio,1-cl_ratio],
                                marker_colors=[roi_color,'rgba(255,255,255,0)']),row=rows_pie[num], col=cols_pie[num])

        # # eccentricity size scatter of sampled data
        idx_sample = df.index[df.roi==roi][np.random.permutation(df[df.roi==roi].shape[0])[0:analysis_info['sample_num']].tolist()]
        fig.append_trace(go.Scatter(x=df.ecc.loc[idx_sample], y=df['size'].loc[idx_sample], mode='markers', showlegend=False, hoverinfo='none',
                                    marker_symbol='circle', marker_size=10, marker_color=adjust_lightness(roi_color, amount=1.25),
                                    marker_line_color='black',marker_line_width = 0.5, marker_opacity=0.2),row=rows_trace[num], col=cols_trace[num])

    # eccentricity/size
    for num,(roi,roi_color) in enumerate(zip(rois,rois_colors)):    
        if df[df['roi']==roi].shape[0] >= 3:
            ecc_size_coeff, ecc_size_intercept = weighted_regression(np.array(df[df.roi==roi].ecc),np.array(df[df.roi==roi]['size']),np.array(df[df.roi==roi].rsq))
            line_y = ecc_size_coeff*line_x+ecc_size_intercept
            fig.append_trace(go.Scatter(x=line_x, y=line_y[0], name = roi, mode='lines', line_width=4, line_color=roi_color, showlegend=False)
                                        ,row=rows_trace[num], col=cols_trace[num])

    # annotations
    fig.add_annotation(xref="paper", yref="paper", x=-0.082, y=0.56, text='Polar<br>angle', showarrow=False, textangle=-90)
    fig.add_annotation(xref="paper", yref="paper", x=-0.082, y=0.435, text='Contra-<br>laterality', showarrow=False, textangle=-90)

    # LAYOUT
    # ------
    fig.layout.update(  # figure settings
                        template=fig_template, width=fig_width, height=fig_height, margin_l=100, margin_r=20, margin_t=50, margin_b=100,
                        # range violin
                        yaxis_range=[0,1], yaxis2_range=[0,1],yaxis3_range=[0,1],yaxis4_range=[0,1], yaxis5_range=[0,1], yaxis6_range=[0,1],
                        yaxis7_range=[0,1],yaxis8_range=[0,1],yaxis9_range=[0,1],yaxis10_range=[0,1],yaxis11_range=[0,1],yaxis12_range=[0,1],
                        # bar polar (uncomment to fix range)
                        # polar_radialaxis_range=barpolar_range,polar2_radialaxis_range=barpolar_range,polar3_radialaxis_range=barpolar_range,
                        # polar4_radialaxis_range=barpolar_range,polar5_radialaxis_range=barpolar_range,polar6_radialaxis_range=barpolar_range,
                        # polar7_radialaxis_range=barpolar_range,polar8_radialaxis_range=barpolar_range,polar9_radialaxis_range=barpolar_range,
                        # polar10_radialaxis_range=barpolar_range,polar11_radialaxis_range=barpolar_range,polar12_radialaxis_range=barpolar_range,
                        # y axis violin
                        yaxis_visible=True, yaxis_linewidth=template_specs['axes_width'], yaxis_title_text='R\u00b2', yaxis_ticklen=8, 
                        # traces #13
                        yaxis13_visible=True, yaxis13_linewidth=template_specs['axes_width'], yaxis13_title_text=y_label_trace, 
                        yaxis13_range=trace_range, yaxis13_ticklen=8, yaxis13_tickvals=trace_tickvals, yaxis13_ticktext=trace_ticktexts,
                        xaxis13_visible=True, xaxis13_linewidth=template_specs['axes_width'], xaxis13_title_text=x_label_trace, 
                        xaxis13_range=trace_range, xaxis13_ticklen=8, xaxis13_tickvals=trace_tickvals, xaxis13_ticktext=trace_ticktexts,
                        # traces #14
                        yaxis14_visible=True, yaxis14_linewidth=template_specs['axes_width'], yaxis14_showticklabels=False, 
                        yaxis14_range=trace_range, yaxis14_ticklen=8, yaxis14_tickvals=trace_tickvals,
                        xaxis14_visible=True, xaxis14_linewidth=template_specs['axes_width'], xaxis14_title_text=x_label_trace, 
                        xaxis14_range=trace_range, xaxis14_ticklen=8, xaxis14_tickvals=trace_tickvals, xaxis14_ticktext=trace_ticktexts,
                        # traces #15
                        yaxis15_visible=True, yaxis15_linewidth=template_specs['axes_width'], yaxis15_showticklabels=False, 
                        yaxis15_range=trace_range, yaxis15_ticklen=8, yaxis15_tickvals=trace_tickvals, 
                        xaxis15_visible=True, xaxis15_linewidth=template_specs['axes_width'], xaxis15_title_text=x_label_trace, 
                        xaxis15_range=trace_range, xaxis15_ticklen=8, xaxis15_tickvals=trace_tickvals, xaxis15_ticktext=trace_ticktexts,)

    return fig