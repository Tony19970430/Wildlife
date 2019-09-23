# Import required libraries
import pickle
import copy
import pathlib
import dash
import dash_table
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import io
import xlsxwriter
import flask
from flask import send_file
import urllib

PATH = pathlib.Path(__file__).parent

app = dash.Dash(
    __name__,
)

server = app.server

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

df = pd.read_csv(PATH.joinpath("comptab_2018-01-29 16_00_comma_separated.csv"))

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

available_exporter = df['Exporter'].unique()
exporter_options_list=[{'label': i, 'value': i} for i in available_exporter]+[{'label': 'All', 'value': 'All'}]
exporter_options_list.pop(35)

available_importer = df['Importer'].unique()
importer_options_list=[{'label': i, 'value': i} for i in available_importer]+[{'label': 'All', 'value': 'All'}]


app.layout = html.Div([


    html.Div([
        html.Div([dcc.Dropdown(id='importer-selector',options=exporter_options_list,value='All')],),
        html.Div([html.H4("Importer")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),
    
    html.Div([
        html.Div([dcc.Dropdown(id='exporter-selector',options=exporter_options_list,value='All')],),
        html.Div([html.H4("Exporter")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),

    html.Div([
        dcc.Graph(
            id='pie-chart-exporter'
        )
    ], className = 'pretty_container six columns'),

], className="pretty_container")


@app.callback(Output('pie-chart-exporter', 'figure'), [Input('exporter-selector', 'value')])
def update_graph(selected):

    df = pd.read_csv(PATH.joinpath("comptab_2018-01-29 16_00_comma_separated.csv"))

    if selected != 'All':
        df = df[df["Exporter"] == selected]

    df_counts = df["Importer"].value_counts().rename_axis('unique_values').reset_index(name='counts')

    return {
        'data': [go.Pie(
            labels=df_counts['unique_values'].values.tolist(),
            values=df_counts["counts"].values.tolist())],
        "layout": go.Layout(autosize=True)}

if __name__ == '__main__':
    app.run_server(debug=True)
