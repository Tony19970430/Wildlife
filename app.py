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

df = pd.read_csv(PATH.joinpath("result.csv"))

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

available_importer = df['Importer'].unique()
importer_options_list=[{'label': i, 'value': i} for i in available_importer]+[{'label': 'All', 'value': 'All'}]
importer_options_list.pop(80)

available_exporter = df['Exporter'].unique()
exporter_options_list=[{'label': i, 'value': i} for i in available_exporter]+[{'label': 'All', 'value': 'All'}]
exporter_options_list.pop(45)

available_source = df['Source'].unique()
source_options_list=[{'label': i, 'value': i} for i in available_source]+[{'label': 'All', 'value': 'All'}]
source_options_list.pop(0)

available_family = df['Family'].unique()
family_options_list=[{'label': i, 'value': i} for i in available_family]+[{'label': 'All', 'value': 'All'}]
family_options_list.pop(35)

available_purpose = df['Purpose'].unique()
purpose_options_list=[{'label': i, 'value': i} for i in available_purpose]+[{'label': 'All', 'value': 'All'}]
purpose_options_list.pop(1)

available_app = df['App.'].unique()
app_options_list=[{'label': i, 'value': i} for i in available_app]+[{'label': 'All', 'value': 'All'}]

available_year = df['Year'].unique()
year_options_list=[{'label': i, 'value': i} for i in available_year]+[{'label': 'All', 'value': 'All'}]



app.layout = html.Div([

    html.Div([
        html.Div([html.H1("Data From CITES Trade Database")], style={"textAlign": "center"}),
        html.Div([html.A("retrieved from https://trade.cites.org/", href='https://trade.cites.org/', target="_blank")]),
        html.Div([html.A("Guide about the codes of the CITES Trade Database could be found here", href='https://trade.cites.org/cites_trade_guidelines/en-CITES_Trade_Database_Guide.pdf', target="_blank")])
    ], className ='pretty_container one-third columns'),

    html.Div([
        html.Div([dcc.Dropdown(id='importer-selector',options=importer_options_list,value='All')],),
        html.Div([html.H4("Importer")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),

    html.Div([
        html.Div([dcc.Dropdown(id='exporter-selector',options=exporter_options_list,value='All')],),
        html.Div([html.H4("Exporter")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),

    html.Div([
        html.Div([dcc.Dropdown(id='source-selector',options=source_options_list,value='All')],),
        html.Div([html.H4("Source")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),

    html.Div([
        html.Div([dcc.Dropdown(id='family-selector',options=family_options_list,value='All')],),
        html.Div([html.H4("Family")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),

    html.Div([
        html.Div([dcc.Dropdown(id='purpose-selector',options=purpose_options_list,value='All')],),
        html.Div([html.H4("Purpose")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),

    html.Div([
        html.Div([dcc.Dropdown(id='app-selector',options=app_options_list,value='All')],),
        html.Div([html.H4("Appendix")], style={"textAlign": "center"})
    ], className ='pretty_container two columns'),

    html.Div([
        dcc.RangeSlider(
            id="year-selector",
            min=1975,
            max=2018,
            value=[1975, 2018],
            ),

        html.Div(id='output-year-selector')], className="pretty_container one-third columns"),
    
    html.Div([
        dcc.Graph(
            id='pie-chart-importer'
        )
    ], className = 'pretty_container four columns'),

    html.Div([
        dcc.Graph(
            id='pie-chart-exporter'
        )
    ], className = 'pretty_container four columns'),

    html.Div([
        dcc.Graph(
            id='pie-chart-source'
        )
    ], className = 'pretty_container four columns'),

    html.Div([
        dcc.Graph(
            id='pie-chart-family'
        )
    ], className = 'pretty_container four columns'),

    html.Div([
        dcc.Graph(
            id='pie-chart-purpose'
        )
    ], className = 'pretty_container four columns'),

    html.Div([
        dcc.Graph(
            id='pie-chart-app'
        )
    ], className = 'pretty_container four columns'),

])

@app.callback(
    dash.dependencies.Output('output-year-selector', 'children'),
    [dash.dependencies.Input('year-selector', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)


@app.callback(Output('pie-chart-importer', 'figure'), [Input('importer-selector', 'value'),Input('exporter-selector', 'value'),
Input('source-selector', 'value'),Input('family-selector', 'value'),Input('purpose-selector', 'value'),Input('app-selector', 'value'),Input('year-selector', 'value')])

def update_graph(selected_importer,selected_exporter,selected_source,selected_family,selected_purpose,selected_app,selected_year):

    df = pd.read_csv(PATH.joinpath("result.csv"))

    df = df[(df["Year"] >= selected_year[0])
        & (df["Year"] <= selected_year[1])
    ]

    if selected_importer != 'All':
        df = df[df["Importer"] == selected_importer]

    if selected_exporter != 'All':
        df = df[df["Exporter"] == selected_exporter]

    if selected_source != 'All':
        df = df[df["Source"] == selected_source]

    if selected_family != 'All':
        df = df[df["Family"] == selected_family]

    if selected_purpose != 'All':
        df = df[df["Purpose"] == selected_purpose]

    if selected_app != 'All':
        df = df[df["App."] == selected_app]

    df_counts = df["Importer"].value_counts().rename_axis('unique_values').reset_index(name='counts')

    return {
        'data': [go.Pie(
            labels=df_counts['unique_values'].values.tolist(),
            values=df_counts["counts"].values.tolist())],
        "layout": go.Layout(title = 'Importer',autosize=True)}

@app.callback(Output('pie-chart-exporter', 'figure'), [Input('importer-selector', 'value'),Input('exporter-selector', 'value'),
Input('source-selector', 'value'),Input('family-selector', 'value'),Input('purpose-selector', 'value'),Input('app-selector', 'value'),Input('year-selector', 'value')])

def update_graph(selected_importer,selected_exporter,selected_source,selected_family,selected_purpose,selected_app,selected_year):

    df = pd.read_csv(PATH.joinpath("result.csv"))

    df = df[(df["Year"] >= selected_year[0])& (df["Year"] <= selected_year[1])]

    if selected_importer != 'All':
        df = df[df["Importer"] == selected_importer]

    if selected_exporter != 'All':
        df = df[df["Exporter"] == selected_exporter]

    if selected_source != 'All':
        df = df[df["Source"] == selected_source]

    if selected_family != 'All':
        df = df[df["Family"] == selected_family]

    if selected_purpose != 'All':
        df = df[df["Purpose"] == selected_purpose]

    if selected_app != 'All':
        df = df[df["App."] == selected_app]

    df_counts = df["Exporter"].value_counts().rename_axis('unique_values').reset_index(name='counts')

    return {
        'data': [go.Pie(
            labels=df_counts['unique_values'].values.tolist(),
            values=df_counts["counts"].values.tolist())],
        "layout": go.Layout(title = 'Exporter',autosize=True)}

@app.callback(Output('pie-chart-source', 'figure'), [Input('importer-selector', 'value'),Input('exporter-selector', 'value'),
Input('source-selector', 'value'),Input('family-selector', 'value'),Input('purpose-selector', 'value'),Input('app-selector', 'value'),Input('year-selector', 'value')])

def update_graph(selected_importer,selected_exporter,selected_source,selected_family,selected_purpose,selected_app,selected_year):

    df = pd.read_csv(PATH.joinpath("result.csv"))

    df = df[(df["Year"] >= selected_year[0])& (df["Year"] <= selected_year[1])]

    if selected_importer != 'All':
        df = df[df["Importer"] == selected_importer]

    if selected_exporter != 'All':
        df = df[df["Exporter"] == selected_exporter]

    if selected_source != 'All':
        df = df[df["Source"] == selected_source]

    if selected_family != 'All':
        df = df[df["Family"] == selected_family]

    if selected_purpose != 'All':
        df = df[df["Purpose"] == selected_purpose]

    if selected_app != 'All':
        df = df[df["App."] == selected_app]

    df_counts = df["Source"].value_counts().rename_axis('unique_values').reset_index(name='counts')

    return {
        'data': [go.Pie(
            labels=df_counts['unique_values'].values.tolist(),
            values=df_counts["counts"].values.tolist())],
        "layout": go.Layout(title = 'Source',autosize=True)}

@app.callback(Output('pie-chart-family', 'figure'), [Input('importer-selector', 'value'),Input('exporter-selector', 'value'),
Input('source-selector', 'value'),Input('family-selector', 'value'),Input('purpose-selector', 'value'),Input('app-selector', 'value'),Input('year-selector', 'value')])

def update_graph(selected_importer,selected_exporter,selected_source,selected_family,selected_purpose,selected_app,selected_year):

    df = pd.read_csv(PATH.joinpath("result.csv"))

    df = df[(df["Year"] >= selected_year[0]) & (df["Year"] <= selected_year[1])]

    if selected_importer != 'All':
        df = df[df["Importer"] == selected_importer]

    if selected_exporter != 'All':
        df = df[df["Exporter"] == selected_exporter]

    if selected_source != 'All':
        df = df[df["Source"] == selected_source]

    if selected_family != 'All':
        df = df[df["Family"] == selected_family]

    if selected_purpose != 'All':
        df = df[df["Purpose"] == selected_purpose]

    if selected_app != 'All':
        df = df[df["App."] == selected_app]

    df_counts = df["Family"].value_counts().rename_axis('unique_values').reset_index(name='counts')

    return {
        'data': [go.Pie(
            labels=df_counts['unique_values'].values.tolist(),
            values=df_counts["counts"].values.tolist())],
        "layout": go.Layout(title='Family',showlegend=False,autosize=True)}

@app.callback(Output('pie-chart-purpose', 'figure'), [Input('importer-selector', 'value'),Input('exporter-selector', 'value'),
Input('source-selector', 'value'),Input('family-selector', 'value'),Input('purpose-selector', 'value'),Input('app-selector', 'value'),Input('year-selector', 'value')])

def update_graph(selected_importer,selected_exporter,selected_source,selected_family,selected_purpose,selected_app,selected_year):

    df = pd.read_csv(PATH.joinpath("result.csv"))

    df = df[(df["Year"] >= selected_year[0]) & (df["Year"] <= selected_year[1])]

    if selected_importer != 'All':
        df = df[df["Importer"] == selected_importer]

    if selected_exporter != 'All':
        df = df[df["Exporter"] == selected_exporter]

    if selected_source != 'All':
        df = df[df["Source"] == selected_source]

    if selected_family != 'All':
        df = df[df["Family"] == selected_family]

    if selected_purpose != 'All':
        df = df[df["Purpose"] == selected_purpose]

    if selected_app != 'All':
        df = df[df["App."] == selected_app]

    df_counts = df["Purpose"].value_counts().rename_axis('unique_values').reset_index(name='counts')

    return {
        'data': [go.Pie(
            labels=df_counts['unique_values'].values.tolist(),
            values=df_counts["counts"].values.tolist())],
        "layout": go.Layout(title = 'Purpose',autosize=True)}

@app.callback(Output('pie-chart-app', 'figure'), [Input('importer-selector', 'value'),Input('exporter-selector', 'value'),
Input('source-selector', 'value'),Input('family-selector', 'value'),Input('purpose-selector', 'value'),Input('app-selector', 'value'),Input('year-selector', 'value')])

def update_graph(selected_importer,selected_exporter,selected_source,selected_family,selected_purpose,selected_app,selected_year):

    df = pd.read_csv(PATH.joinpath("result.csv"))

    df = df[(df["Year"] >= selected_year[0]) & (df["Year"] <= selected_year[1])]

    if selected_importer != 'All':
        df = df[df["Importer"] == selected_importer]

    if selected_exporter != 'All':
        df = df[df["Exporter"] == selected_exporter]

    if selected_source != 'All':
        df = df[df["Source"] == selected_source]

    if selected_family != 'All':
        df = df[df["Family"] == selected_family]

    if selected_purpose != 'All':
        df = df[df["Purpose"] == selected_purpose]

    if selected_app != 'All':
        df = df[df["App."] == selected_app]

    df_counts = df["App."].value_counts().rename_axis('unique_values').reset_index(name='counts')

    return {
        'data': [go.Pie(
            labels=df_counts['unique_values'].values.tolist(),
            values=df_counts["counts"].values.tolist())],
        "layout": go.Layout(title = 'Appendix',autosize=True)}

if __name__ == '__main__':
    app.run_server(debug=True)
