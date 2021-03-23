# TO DO
# 1. change style of text to adjust the figures
# 2. change alignment of rangeslider to a fixed location
# 3. make multiple comparison plots ?

# General imports
import warnings
import numpy as np
import pandas as pd
from .dashboards import prf_dashboard

# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

# stop warnings
warnings.filterwarnings("ignore")

# define exp settings
rsqr_th, size_th, ecc_th = [0.1,1], [0.1,15], [0.1,15]
subject_list = ["sub-001","sub-002","sub-003","sub-004","sub-005","sub-006","sub-007","sub-008"]
task_list = ['GazeCenterFS']
preproc_list = ['fmriprep_dct','fmriprep_dct_pca']

# define styles
style_rangeslider = {   'display': "grid", 'text-align':'left',
                        'grid-template-columns': "150px 100px 950px",
                        'margin-top': 25}
style_dropdown_title = {'display': "grid", 'text-align':'left',
                        'grid-template-columns': "575px 50px 575px",
                        'margin-bottom': 25}
style_dropdown = {      'display': "grid", 'text-align':'left',
                        'grid-template-columns': "150px 425px 50px 150px 425px",
                        'margin-bottom': 0}

# define dropdown options
subject_options = []
for subject in subject_list: subject_options.append({'label': subject, 'value': subject})
task_options = []
for task in task_list: task_options.append({'label': task, 'value': task})
preproc_options = []
for preproc in preproc_list: preproc_options.append({'label': preproc, 'value': preproc})


# define layout
layout = html.Div(children=[
    
    # dropdowns
    html.Div(children=[ dcc.Markdown("__DASHBOARD #1__"),
                        html.Spacer(),
                        dcc.Markdown("__DASHBOARD #2__")],
             style=style_dropdown_title),

    html.Div(children=[ dcc.Markdown("__Subject__", style={'margin-top': 5}),
                        dcc.Dropdown(id='subject_dd_1', options=subject_options, value=subject_list[0]),
                        html.Spacer(),
                        dcc.Markdown("__Subject__", style={'margin-top': 5}),
                        dcc.Dropdown(id='subject_dd_2', options=subject_options, value=subject_list[1])],
             style=style_dropdown),

    html.Div(children=[ dcc.Markdown("__Preprocessing__", style={'margin-top': 5}),
                        dcc.Dropdown(id='preproc_dd_1', options=preproc_options, value=preproc_list[0]),
                        html.Spacer(),
                        dcc.Markdown("__Preprocessing__", style={'margin-top': 5}),
                        dcc.Dropdown(id='preproc_dd_2', options=preproc_options, value=preproc_list[0])],
             style=style_dropdown),

    html.Div(children=[ dcc.Markdown("__Task__", style={'margin-top': 5}),
                        dcc.Dropdown(id='task_dd_1', options=task_options, value=task_list[0]),
                        html.Spacer(),
                        dcc.Markdown("__Task__", style={'margin-top': 5}),
                        dcc.Dropdown(id='task_dd_2', options=task_options, value=task_list[0])],
             style=style_dropdown),

    # main figure
    dcc.Tabs([dcc.Tab(  label='Dashboard #1', 
                        children=[  dcc.Graph(  id='prf_dashboard_1',
                                                config={'displayModeBar': False},
                                                style= {'width': "1200px"})]),
             dcc.Tab(   label='Dashboard #2', 
                        children=[  dcc.Graph(  id='prf_dashboard_2',
                                                config={'displayModeBar': False},
                                                style= {'width': "1200px"})])],
             style= {'margin-top': 20,
                     'width': "1200px"}),

    # rsq range slider
    html.Div(children=[ dcc.Markdown("__R\u00b2__"),
                        dcc.Markdown(id='rsq_slider_text'),
                        dcc.RangeSlider(id='rsq_slider', min=0, max=1, step=0.05, updatemode='mouseup',
                                        value=[rsqr_th[0],rsqr_th[1]], marks={0:'0', 0.5:'0.5', 1:'1'})],
            style=style_rangeslider),

    # eccentricity range slider
    html.Div(children=[ dcc.Markdown("__Eccentricity (dva)__"),
                        dcc.Markdown(id='ecc_slider_text'),
                        dcc.RangeSlider(id='ecc_slider', min=0, max=20, step=0.1, updatemode='mouseup',
                                        value=[ecc_th[0],ecc_th[1]], marks={0:'0',5:'5',10:'10',15:'15',20:'20'})],
            style=style_rangeslider),

    # size range slider
    html.Div(children=[ dcc.Markdown('__Size (dva)__'),
                        dcc.Markdown(id='size_slider_text'),
                        dcc.RangeSlider(id='size_slider', min=0, max=20, step=0.1, updatemode='mouseup',
                                        value=[size_th[0],size_th[1]],marks={0:'0',5:'5',10:'10',15:'15',20:'20'})],
             style=style_rangeslider),

    ])

# define callbacks
@app.callback(Output('rsq_slider_text', 'children'),
              Output('ecc_slider_text', 'children'),
              Output('size_slider_text', 'children'),
              Output('prf_dashboard_1', 'figure'),
              Output('prf_dashboard_2', 'figure'),
              Input('rsq_slider', 'value'),
              Input('ecc_slider', 'value'),
              Input('size_slider', 'value'),
              Input('subject_dd_1','value'),
              Input('preproc_dd_1','value'),
              Input('task_dd_1','value'),
              Input('subject_dd_2','value'),
              Input('preproc_dd_2','value'),
              Input('task_dd_2','value'),
              )

def update_dashboard(rsq_slider_value, 
                     ecc_slider_value, 
                     size_slider_value, 
                     subject_1, 
                     preproc_1, 
                     task_1,
                     subject_2, 
                     preproc_2, 
                     task_2):

    txt_rsq = '\[{} / {}\]'.format(rsq_slider_value[0],rsq_slider_value[1])
    txt_ecc = '\[{} / {}\]'.format(ecc_slider_value[0],ecc_slider_value[1])
    txt_size = '\[{} / {}\]'.format(size_slider_value[0],size_slider_value[1])

    # dashboard 1
    df_1_name = 'apps/data/{}_{}_{}.gz'.format(subject_1, task_1, preproc_1)
    df_1_raw = pd.read_csv(df_1_name)
    df_1 = df_1_raw[(df_1_raw.rsq >= rsq_slider_value[0]) & (df_1_raw.rsq <= rsq_slider_value[1]) & 
                    (df_1_raw['size'] >= size_slider_value[0]) & (df_1_raw['size'] <= size_slider_value[1]) & 
                    (df_1_raw.ecc >= ecc_slider_value[0]) & (df_1_raw.ecc <= ecc_slider_value[1])]
    fig_1 = prf_dashboard(df_1)

    # dashboard 2
    df_2_name = 'apps/data/{}_{}_{}.gz'.format(subject_2, task_2, preproc_2)
    df_2_raw = pd.read_csv(df_2_name)
    df_2 = df_2_raw[(df_2_raw.rsq >= rsq_slider_value[0]) & (df_2_raw.rsq <= rsq_slider_value[1]) & 
                    (df_2_raw['size'] >= size_slider_value[0]) & (df_2_raw['size'] <= size_slider_value[1]) & 
                    (df_2_raw.ecc >= ecc_slider_value[0]) & (df_2_raw.ecc <= ecc_slider_value[1])]
    fig_2 = prf_dashboard(df_2)

    return [txt_rsq, txt_ecc, txt_size, fig_1, fig_2]