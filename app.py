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


df1 = pd.read_csv(PATH.joinpath("comptab_2019-09-23 19_38_comma_separated.csv"))
df2 = pd.read_csv(PATH.joinpath("comptab_2019-09-23 19_41_comma_separated.csv"))

result = pd.concat([df1,df2])

result = result.reset_index(drop=True)
result.to_csv('result.csv', index = False)