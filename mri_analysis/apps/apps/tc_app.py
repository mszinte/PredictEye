# to do 
# 1. make filter by R2 / ECC / SIZE
# 2. make button to switch between voxel corresponding to the selection

# General imports
import warnings
import numpy as np
import pandas as pd
from .dashboards import tc_plot

# Dash imports
import dash, json
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
import ipdb

deb = ipdb.set_trace
# Define analysis parameters
with open('apps/settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# define styles
style_dropdown = {     'display': "grid", 
                        'text-align':'left',
                        'grid-template-columns': "70px 420px 20px 70px 420px",
                        'margin-bottom': 0}

# define exp settings
rsqr_th, size_th, ecc_th = analysis_info['rsqr_th'], analysis_info['size_th'], analysis_info['ecc_th']
roi_list = analysis_info['rois']
subject_list = analysis_info['subject_list']
task_list = analysis_info['task_list']
sub_task_list = analysis_info['sub_task_list']
preproc_list = analysis_info['preproc']
reg_list = analysis_info['registration_type']

TR = 208
numplot = 0

# define dropdown options
roi_options = []
for roi in roi_list: roi_options.append({'label': roi, 'value': roi})
subject_options = []
for subject in subject_list: subject_options.append({'label': subject, 'value': subject})
task_options = []
for task in task_list: task_options.append({'label': task, 'value': task})
sub_task_options = []
for sub_task in sub_task_list: sub_task_options.append({'label': sub_task, 'value': sub_task})
preproc_options = []
for preproc in preproc_list: preproc_options.append({'label': preproc, 'value': preproc})
reg_options = []
for reg in reg_list: reg_options.append({'label': reg, 'value': reg})

# define layout
layout = html.Div(children=[

    # dropdowns
    html.Div(children=[ dcc.Markdown(   "__Subject__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='subject_dd', 
                                        options=subject_options, 
                                        value=subject_list[0]),
                        html.Spacer(),
                        dcc.Markdown(   "__ROI__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='roi_dd', 
                                        options=roi_options, 
                                        value=roi_list[0])
                        ],
            style=style_dropdown),
    
    html.Div(children=[ dcc.Markdown(   "__Task__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='task_dd', 
                                        options=task_options, 
                                        value=task_list[1]),
                        html.Spacer(),
                        dcc.Markdown(   "__Subtask__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='sub_task_dd', 
                                        options=sub_task_options, 
                                        value=sub_task_list[1])
                        ],
            style=style_dropdown),


    html.Div(children=[ dcc.Markdown(   "__PP__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='preproc_dd', 
                                        options=preproc_options, 
                                        value=preproc_list[0]),
                        html.Spacer(),
                        dcc.Markdown(   "__Reg.__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='reg_dd', 
                                        options=reg_options, 
                                        value=reg_list[0]),
                        ],
            style=style_dropdown),
    

    # main figure
    dcc.Graph(  id='tc_dashboard',
                config={'displayModeBar': False},
                style={'height': "250", 'width': "1000"}),

    # r2 range slider
    html.Div(children=  [   dcc.Markdown("__R\u00b2__ &nbsp"),
                            dcc.Markdown(id='r2_slider_text'),
                            dcc.RangeSlider(id='r2_slider',
                                            min=0, max=1,step=0.05,
                                            value = [rsqr_th[0],rsqr_th[1]],
                                            updatemode='mouseup',
                                            marks={0:'0', 0.5:'0.5', 1:'1'})],
            style={ 'text-align':'right',
                    'display': "grid", 
                    'grid-template-columns': "150px 50px 800px",
                    'margin-top': 25}),

    ]
)

@app.callback(Output('tc_dashboard', 'figure'),
              Input('subject_dd','value'),
              Input('task_dd','value'),
              Input('sub_task_dd','value'),
              Input('preproc_dd','value'),
              Input('reg_dd','value'),
              Input('roi_dd','value'),
              )

def update_dashboard(subject, task, sub_task, preproc, reg, roi):

    # load data
    df_name = "apps/data/{}/{}{}/{}_{}_{}.gz".format(subject,task,sub_task,roi,preproc,reg)
    df = pd.read_pickle(df_name,compression='gzip')

    # plot figue
    tc_fig = tc_plot(df,numplot)

    return tc_fig