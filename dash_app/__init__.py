import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from flask import Flask

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})
server = Flask(__name__)
dash_app_lay = dash.Dash(__name__,server=server)

dash_app_lay.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
    ),
    html.Div(id='example'),
])

@dash_app_lay.callback(Output('example', 'figure'))
def callback_z():
    return html.P('Arunkumar')

@server.route('/dash/')
def myDashApp():
    return dash_app_lay