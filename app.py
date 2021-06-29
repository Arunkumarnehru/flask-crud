from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import requests
from datetime import date, timedelta
# dashboard 
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json
from flask_migrate import Migrate
from sqlalchemy import  create_engine
from werkzeug.utils import secure_filename

# from dash_app import my_dash_app

app = Flask(__name__, template_folder='templates')  # still relative to module
app.secret_key = "Secret Key"

# SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Arun123@localhost/employee'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate()
db.init_app(app)
migrate.init_app(app, db)
# my_dash_app(app)
# Creating model table for our CRUD database
class Data(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    department = db.Column(db.String(100), nullable=True)
    salary = db.Column(db.Integer, nullable=True)
    experience = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.Text)

    def __init__(self, name, email, phone, department, salary, experience, profile_picture):
        self.name = name
        self.email = email
        self.phone = phone
        self.department = department
        self.salary = salary
        self.experience = experience
        self.profile_picture = profile_picture

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(200))
    date = db.Column(db.Date)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))


@app.route('/')
def index():
    all_data = Data.query.all()
    return render_template("index.html", employees=all_data)
import base64

# this route is for inserting data to mysql database via html forms
def render_picture(data):
    
    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic
@app.route('/insert', methods=['POST'])
def insert():

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']
        salary = request.form['salary']
        experience = request.form['experience']
        profile_pic = request.files['profile_picture']
        print('profile_pic', profile_pic)
        profile_picture= profile_pic.read()
        print('profile_picture', profile_picture)
        my_data = Data(name, email, phone, department, salary, experience, profile_picture)
        db.session.add(my_data)
        db.session.commit()
        flash("Employee Inserted Successfully")
        return redirect(url_for('index'))
# this is our update route where we are going to update our employee


@app.route('/update', methods=['GET', 'POST'])
def update():

    if request.method == 'POST':
        my_data = Data.query.get(request.form.get('id'))

        my_data.name = request.form['name']
        my_data.email = request.form['email']
        my_data.phone = request.form['phone']
        my_data.department = request.form['department']
        my_data.salary = request.form['salary']
        my_data.experience = request.form['experience']
        db.session.commit()
        flash("Employee Updated Successfully")

        return redirect(url_for('index'))


# This route is for deleting our employee
@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Employee Deleted Successfully")

    return redirect(url_for('index'))

# @app.route('/leave_add', methods=['POST'])
# def leave_insert():

#     if request.method == 'POST':
#         reason = request.form['reason']
#         date = request.form['date']
#         employee_id = request.form['employee_id']
#         my_data = Data(reason, date, employee_id)
#         db.session.add(my_data)
#         db.session.commit()
#         flash("Leave Inserted Successfully")
#         return redirect(url_for('index'))


@app.route('/weather_html/')
def weather_html():
    return render_template("weather_html.html")

# This route is for check weather
@app.route('/weather/', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        city = request.form['city']
        api_address='http://api.openweathermap.org/data/2.5/weather?appid=85c82086e072fb015eca1a62d3989d88&q='
        url = api_address + city
        json_data = requests.get(url).json()
        temp = ((json_data['main']['temp']) - 273.15)
        max_temp = json_data['main']['temp_min']
        min_temp = json_data['main']['temp_max']
        wind = json_data['wind']['speed']
        clouds = json_data['weather'][0]['description']
        img = json_data['weather'][0]['icon']
        img_url = "http://openweathermap.org/img/w/"+img+".png"
        we_v = [round(temp), wind, clouds,city,img_url]
        return render_template('weather.html', weather=we_v)

# next 4 days        
# This route is for check weather
@app.route('/forecast/', methods=['GET', 'POST'])
def forecast():
    if request.method == 'POST':
        city = request.form['city']
        api_key = '85c82086e072fb015eca1a62d3989d88'
        api_address='http://api.openweathermap.org/data/2.5/forecast?q=%s&appid=%s' % (city, api_key)
        json_data = requests.get(api_address).json()
        datas = json_data['list']       
        my_dict = {"temp":[],"date":[],"desc":[],"wind":[],"city":[]}
        for data in datas:
            my_dict["temp"].append((data['main']['temp'])-273.15)
            my_dict["date"].append(data['dt_txt'])
            my_dict['desc'].append(data['weather'][0]['description'])
            my_dict['wind'].append(data['wind']['speed'])
            my_dict['city'].append(city)
        return render_template('forecast.html', weather=my_dict)

@app.route('/location/', methods=['GET', 'POST'])
def location():
    if request.method == 'POST':
        lat = request.form['lat']
        lon = request.form['lon']
        selection = request.form['exclude']
        if selection == 'current':
            exclude = 'minutely,hourly,daily'
        if selection == 'minutely':
            exclude = 'hourly,daily'
        if selection == 'hourly':
            exclude = 'minutely,daily'
        if selection == 'daily':
            exclude = 'minutely,hourly'          
        api_key = '85c82086e072fb015eca1a62d3989d88'
        api_address='http://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&exclude=%s&appid=%s' % (lat,lon,exclude,api_key)
        print(api_address)
        json_data = requests.get(api_address).json()
        temp = ((json_data['current']['temp']) - 273.15)
        return render_template('location.html', weather=temp, context=json_data)

@app.route('/days/', methods=['GET', 'POST'])
def days():
    if request.method == 'POST':
        lat = request.form['lat']
        lon = request.form['lon']
        selection = request.form['dt']
        today = date.today()
        if selection == 'yesterday':
            day_range = 1
        if selection == 'last 2 days':
            day_range = 2
        if selection == 'last 3 days':
            day_range = 3
        if selection == 'last 4 days':
            day_range = 4
        for i in range(day_range):
            day = today - timedelta(days=i)
        ts = day.strftime("%s")
        api_key = '85c82086e072fb015eca1a62d3989d88'
        api_address='http://api.openweathermap.org/data/2.5/onecall/timemachine?lat=%s&lon=%s&dt=%s&appid=%s' % (lat,lon,ts,api_key)
        json_data = requests.get(api_address).json()
        temp = ((json_data['current']['temp']) - 273.15)
        return redirect(api_address)
        # return render_template('days.html', weather=temp, context=json_data)

def create_plot():
    # all_data = Data.query.with_entities(Data.department).order_by(Data.department)
    salary_query = Data.query.with_entities(Data.name, Data.salary).order_by(Data.name)
    print(salary_query)
    x,y=[],[]
    for row in salary_query:
        y.append(row.name)
        x.append(row.salary)
    df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe

    data = [
        go.Bar(
            x=df['x'], # assign x as the dataframe column 'x'
            y=df['y'],
            orientation='h'
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


# def exp_chart():
#     exp_query = Data.query.with_entities(Data.name, Data.experience).order_by(Data.name)
#     print(exp_query)
#     x,y=[],[]
#     for row in exp_query:
#         x.append(row.name)
#         y.append(row.experience)
#     df = pd.DataFrame({'x': x, 'y': y})

#     data = [
#         go.Bar(
#             x=df['x'],
#             y=df['y']
#         )
#     ]
#     graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
#     return graphJSON
# @app.route('/chart')
# def sample_chart():
#     bar = create_plot()
#     exp_bar = exp_chart()
#     return render_template('chart.html', plot=bar, plot2=exp_bar )
server = Flask(__name__)
graph_app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
    suppress_callback_exceptions = True,
    prevent_initial_callbacks=True
)

import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State


# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

graph_app.layout = html.Div(children=[
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

@graph_app.callback(Output('example', 'figure'))
def callback_z():
    return html.P('Arunkumar')

# @app.route("/dash/")
# def my_dash_app():
#     return graph_app()

if __name__ == "__main__":
    app.run(threaded=True, port=5000)