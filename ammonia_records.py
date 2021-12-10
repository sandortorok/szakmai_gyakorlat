import dash_bootstrap_components as dbc
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import mydatabase as db
import plotly.express as px
import pandas as pd
import datetime, calendar
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from collections import Counter


class RecordTab:
    def __init__(self, app):
        self.database = db.SensorDB()
        self.app = app
        self.how_old = 0
        self.createLayout()
        self.graph()
    def createSensorSelector(self):
        drop_options = []
        sensor_numbers = self.database.getSensorNumbers()
        for i in sensor_numbers:
            drop_options.append({'label': 'sensor {}'.format(i[0]), 'value': i[0]})
        dropdown =  dcc.Dropdown(
            options=drop_options,
            className="dash-bootstrap",
            multi=True,
            id = 'sensor-select-dropdown'
        )
        return dropdown
    def createRadioItems(self):
        rad =  dbc.RadioItems(
                id="graph-scale",
                className="btn-group",
                labelClassName="btn btn-secondary",
                labelCheckedClassName="active",
                options=[
                    {"label": "H", "value": 1},
                    {"label": "D", "value": 2},
                    {"label": "W", "value": 3},
                    {"label": "M", "value": 4},
                    {"label": "Y", "value": 5}
                ],
                value=1,
            )
        return rad
    def createLayout(self):
        self.layout = html.Div([
            html.Div(
                [
                    self.createSensorSelector(),
                    self.createRadioItems(),
                    dcc.DatePickerSingle(
                        id='date-picker',
                        min_date_allowed=datetime.datetime(2000, 1, 1),
                        max_date_allowed=datetime.datetime.today(),
                        initial_visible_month=datetime.datetime.today(),
                        date=datetime.datetime.today()
                    ),
                    dbc.ButtonGroup(
                        [dbc.Button(html.I(className='fa fa-angle-double-left'), id= 'graph-left'), 
                         dbc.Button(html.I(className='fa fa-angle-double-right'), id = 'graph-right')],
                        style={'float': 'right'}
                    )
                ],
                style={'marginTop': '1%'}
            ),

            dcc.Graph(id='sensor_record_graph'),
            dcc.Interval(
                id='graph-interval-component-2',
                interval=1*1000, # in milliseconds
                n_intervals=0
            )
        ]
        , className='radio-group')
    def graph(self):
        self.app.callback(
            Output('sensor_record_graph', 'figure'),
            Input('graph-scale', 'value'),
            Input('graph-right', 'n_clicks'), Input('graph-left', 'n_clicks'),
            Input('sensor-select-dropdown','value'),
            Input('date-picker', 'date')
        )(self.graph_callback)
    def graph_callback(self, val, right, left, sensors_selected, date_picked):
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        else:
            button_id = ''
        if button_id == 'graph-right':
            self.how_old -=1
        elif button_id == 'graph-left':
            self.how_old +=1
        elif button_id == 'graph-scale':
            self.how_old = 0

        elif button_id == 'date-picker':
            self.how_old = 0
        
        if not sensors_selected:
            none_selected = True
        else:
            none_selected = False
        if val == 1:
            date = datetime.datetime.strptime(date_picked[:10], '%Y-%m-%d')-datetime.timedelta(days=self.how_old)
            str_date = "'" + str(date.date()) + "'"
            df = pd.DataFrame(self.database.hourlyAverage(str_date))
            if df.empty or none_selected:
                fig = go.Figure()
                arr1 = ["0 óra","24 óra"]
                arr2 = [None, None]
                fig.add_trace(go.Scatter(x=arr1, y=arr2,
                    mode='lines+markers'))
                fig.update_xaxes(categoryorder='category ascending')
                fig.update_layout(
                    title="Hourly View",
                    xaxis_title="{} hours".format(date.date()),
                    yaxis_title="Average Ammonia level",
                    legend_title="Sensor id_s",
                )
                return fig
            else:
                for i in range (len(df)):
                    date = str(df[1][i])[:-3]
                    hour = str(df[1][i])[-2:]
                    df[1][i] = "{} óra".format(hour)
                fig = go.Figure()
                for i in sensors_selected:
                    new_df = df[df[0] == i]
                    fig.add_trace(go.Scatter(x=new_df[1], y=new_df[2],
                        mode='lines+markers',
                        name = '{}'.format(i)))
                fig.update_xaxes(categoryorder='category ascending')
                fig.update_layout(
                    title="Hourly View",
                    xaxis_title="{} hours".format(date),
                    yaxis_title="Average Ammonia level",
                    legend_title="Sensor id_s",
                )
                return fig
        if val == 2:
            df = pd.DataFrame(self.database.dailyAverage(self.how_old))
            if df.empty or none_selected:
                today = datetime.date.today()
                current_day = today - datetime.timedelta(days=7*self.how_old)
                week_number = current_day.isocalendar()[1]
                year_number = current_day.year
                firstdayofweek = datetime.datetime.strptime(f'{year_number}-W{int(week_number-1)}-1', "%Y-W%W-%w").date()
                lastdayofweek = firstdayofweek + datetime.timedelta(days=6.9)

                firstdayofweek = firstdayofweek - datetime.timedelta(days=1) #had to adjust to the graph
                lastdayofweek = lastdayofweek - datetime.timedelta(days=1)

                arr2 = [firstdayofweek,lastdayofweek]
                arr = [None, None]
                fig = px.line(x=arr2, y=arr)
                fig.update_layout(
                    title="Daily View"
                )
                return fig
            else:
                fig = go.Figure()
                colors = sensors_selected
                for i in colors:
                    new_df = df[df[0] == i]
                    fig.add_trace(go.Scatter(x=new_df[1], y=new_df[2],
                        mode='lines+markers',
                        name = 'sensor {}'.format(i)))
                    fig.update_layout(
                        title="Daily View"
                    )
                return fig
        if val == 3:
            df = pd.DataFrame(self.database.weeklyAverage(self.how_old))
            if df.empty or none_selected:
                todays_date = datetime.date.today()
                m = todays_date.month - self.how_old
                y = todays_date.year

                while m <= 0:
                    m += 12
                    y -= 1
                while m > 12:
                    m -= 12
                    y += 1
                num_days = calendar.monthrange(y, m)[1]
                dates_in_month = [datetime.date(y, m, day) for day in range(1, num_days+1)]
                arr1 = []
                for i in dates_in_month:
                    week_number = i.isocalendar()[1]
                    formatted_week = "{}.year {}.week".format(y, week_number)
                    arr1.append(formatted_week)
                arr2 = []
                for i in arr1:
                    arr2.append(None)
                fig = px.line(x=arr1, y=arr2)
                fig.update_layout(
                    title="Weekly View"
                )
                return fig
            else:
                for i in range(0, len(df[1])):
                    year = str(df[1][i])[0:4]
                    week = str(df[1][i])[4:6]
                    df[1][i] = "{}.year {}.week".format(year, week)
                fig = go.Figure()
                colors = sensors_selected
                for i in colors:
                    new_df = df[df[0] == i]
                    fig.add_trace(go.Scatter(x=new_df[1], y=new_df[2],
                        mode='lines+markers',
                        name = 'sensor {}'.format(i)))
                    fig.update_layout(
                        title="Weekly View"
                    )
                    fig.update_xaxes(categoryorder='category ascending')
                return fig
        if val == 4:
            df = pd.DataFrame(self.database.monthlyAverage(self.how_old))
            if df.empty or none_selected:
                dates = []
                for i in range(1,13):
                    x = datetime.datetime(datetime.date.today().year - self.how_old, i, 1)
                    dates.append(x)
                arr = []
                for i in range (len(dates)):
                    arr.append(None)
                fig = px.line(x=dates, y=arr)
                fig.update_layout(
                    title="Monthly View"
                )
                return fig
            else:
                fig = go.Figure()
                for i in sensors_selected:
                    new_df = df[df[0] == i]
                    fig.add_trace(go.Scatter(x=new_df[1], y=new_df[2],
                        mode='lines+markers',
                        name = 'sensor {}'.format(i)))
                    fig.update_layout(
                        title="Monthly View"
                    )
                return fig
        if val == 5:
            df = pd.DataFrame(self.database.yearlyAverage())
            if none_selected:
                raise PreventUpdate
            for i in range(0, len(df[1])):
                df[1][i] = str(df[1][i])[:-3]
            fig = go.Figure()
            for i in sensors_selected:
                new_df = df[df[2] == i]
                fig.add_trace(go.Scatter(x=new_df[1], y=new_df[0],
                    mode='lines+markers',
                    name = 'sensor {}'.format(i)))
                fig.update_layout(
                    title="Yearly View"
                )
            return fig

#WILL DELETE THESE
# external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
# app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
# B = RecordTab(app)
# app.layout = B.layout
# server = app.server