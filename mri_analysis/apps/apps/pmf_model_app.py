# General imports
import warnings
import itertools, os
import numpy as np
import pandas as pd
from .utils import save_motor_design
from .dashboards import plot_motor_design

# Dash imports
import dash, json
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app
import ipdb
deb = ipdb.set_trace

# Define parameters
with open('apps/settings.json') as f:
    json_s = f.read()
    analysis_info = json.loads(json_s)

# define styles
style_dropdown = {  'display': "grid", 
                    'text-align':'center',
                    'grid-template-columns': "70px 420px 20px 70px 420px",
                    'margin-bottom': 0}

style_slider={  'text-align':'center',
                'display': "grid", 
                'grid-template-columns': "100px 100px 800px",
                'margin-top': 25}

# define exp settings

# define dropdown options
# input (temp)
sub_tasks = ['sp','sac']
sac_radial_sd = [0.25,0.25,0.25,0.25]
sac_tangential_sd = [0.25,0.25,0.25,0.25]
sp_radial_sd = [0.25,0.25,0.25,0.25]
sp_tangential_sd = [0.25,0.25,0.25,0.25]
eyemov_sd = [sp_radial_sd,sp_tangential_sd,sac_radial_sd,sac_tangential_sd]
#save_motor_design(sub_tasks,eyemov_sd)

seq_num = 1
permut = itertools.permutations([1, 2, 3, 4])
amp_eyemov = np.linspace(2.5,10,4)
seq_options = []

sub_task_options = []
for sub_task_val in sub_tasks:
    sub_task_options.append({'label': "pMF{}".format(sub_task_val), 'value': sub_task_val})

for seq_num, seq in enumerate(permut):
    value_val = seq_num
    label_val = "{:1.1f} dva / {:1.1f} dva / {:1.1f} dva / {:1.1f} dva".format(amp_eyemov[seq[0]-1],amp_eyemov[seq[1]-1],amp_eyemov[seq[2]-1],amp_eyemov[seq[3]-1])
    seq_options.append({'label': label_val, 'value': value_val})    

# define layout
layout = html.Div(children=[

    # dropdowns
    html.Div(children=[ dcc.Markdown(   "__Task__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='sub_task_dd', 
                                        options=sub_task_options, 
                                        value=sub_tasks[1]),
                        html.Spacer(),
                        dcc.Markdown(   "__Seq.__", 
                                        style={'margin-top': 5}),
                        dcc.Dropdown(   id='seq_dd', 
                                        options=seq_options, 
                                        value=0)
                        ],
            style=style_dropdown),

    # motor design
    dcc.Graph(  id='motor_design_dashboard',
                config={'displayModeBar': False},
                style={'height': "250", 'width': "1000"}),

    # ecc slider
    html.Div(children=  [   dcc.Markdown("__pMF ecc.__"),
                            dcc.Markdown(id='ecc_slider_val'),
                            dcc.Slider(id='ecc_slider',
                                       min=0, max=15,step=0.1,
                                       value = 2.5,
                                       updatemode='mouseup',
                                       marks={0:'0', 5:'5', 10:'10', 15:'15'})],
            style=style_slider),

    # size slider
    html.Div(children=  [   dcc.Markdown("__pMF size__"),
                            dcc.Markdown(id='size_slider_val'),
                            dcc.Slider(id='size_slider',
                                       min=0, max=15,step=0.1,
                                       value = 0.5,
                                       updatemode='mouseup',
                                       marks={0:'0', 5:'5', 10:'10', 15:'15'})],
            style=style_slider),
    
    # angle slider
    html.Div(children=  [   dcc.Markdown("__pMF angle__"),
                            dcc.Markdown(id='angle_slider_val'),
                            dcc.Slider(id='angle_slider',
                                       min=0, max=360,step=1,
                                       value = 180,
                                       updatemode='mouseup',
                                       marks={0:'0', 90:'90', 180:'180', 270:'270', 360:'360'})],
            style=style_slider),
    
    # export button
    html.Div(children=  [   dcc.Markdown("__Directory__",style = {'margin-top': 5}),
                            dcc.Input(  id='directory_input', 
                                        type='text',
                                        value='figures/figure.pdf'),
                            html.Button('Export as .pdf', 
                                        id='export_button', 
                                        n_clicks=0)],
            style ={  'text-align':'center',
                        'display': "grid", 
                        'grid-template-columns': "100px 700px 200px",
                        'margin-top': 25,
                        'margin-bottom': 0}),

    ]
    
)

pmf_ecc = 0
pmf_angle = 90
pmf_size = 2

# define callback
@app.callback(  Output('motor_design_dashboard', 'figure'),
                Output('ecc_slider_val', 'children'),
                Output('size_slider_val', 'children'),
                Output('angle_slider_val', 'children'),
                Input('sub_task_dd','value'),
                Input('seq_dd','value'),
                Input('ecc_slider', 'value'),
                Input('size_slider', 'value'),
                Input('angle_slider', 'value'),
                Input('export_button', 'n_clicks'),
                State('directory_input', 'value')
             )

# define updates
def update_dashboard(sub_task, seq_num, ecc_slider_value, size_slider_value, angle_slider_value, n_cliks, dir_val):

    
    motor_design_fig = plot_motor_design(   sub_task=sub_task,
                                            seq_num=seq_num+1,
                                            pmf_ecc=ecc_slider_value, 
                                            pmf_size=size_slider_value,
                                            pmf_angle=angle_slider_value)

    txt_ecc = '{} dva'.format(ecc_slider_value)
    txt_size = '{} dva'.format(size_slider_value)
    txt_angle = '{} deg'.format(angle_slider_value)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'export_button' in changed_id:
        print('Figure saved : {}'.format(dir_val))
        motor_design_fig.write_image(dir_val, width=1000, height=500)
        



    return motor_design_fig, txt_ecc, txt_size, txt_angle