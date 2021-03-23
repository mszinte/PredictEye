import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import tc_app, pmf_model_app

app.layout = html.Div(children=
    [   dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))

def display_page(pathname):
    if pathname == '/apps/tc_app':
        return tc_app.layout
    elif pathname == '/apps/pmf_model_app':
        return pmf_model_app.layout
    else:
        return "404 Page Error! Please choose a link"

if __name__ == '__main__':
    app.run_server(debug=True)