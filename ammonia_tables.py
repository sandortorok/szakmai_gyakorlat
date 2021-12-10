import mydatabase as db
import dash_bootstrap_components as dbc
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import COM
import threading
import json
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import redis
from datetime import datetime, timedelta
import ammonia_reader as rd
import math

# Shut down the scheduler when exiting the app
class tablesTab: 
    def __init__(self, app):
        self.modalid = "table-modal"
        self.closeid = "modal-close"
        self.hornid = "modal-horn"
        self.database = db.SensorDB()
        self.redis_client = redis.Redis(host='localhost', port='6379')
        self.app = app
        self.lock = threading.Lock()
        self.reader = rd.Read()
        self.sensornumber = self.reader.tablesInit()[0]
        self.COMPORT = COM.ComPacket(self.sensornumber)

        scheduler = BackgroundScheduler()
        scheduler.add_job(func=self.updating, trigger="interval", seconds = 0.1, max_instances= 5)
        scheduler.add_job(func=self.disksave, trigger='interval', minutes = 1, max_instances= 5)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
        self.mergeTable()
        self.call_callbacks()
    def disksave(self):
        this_minute = datetime.now().strftime("%Y-%m-%d-%H-%M")
        for i in range(self.sensornumber):
            data = self.redis_client.keys("*"+"sensor_"+str(i+1)+":"+this_minute+"*")

            sum = 0
            data_amount = 0
            for element in data:
                val =int(self.redis_client.get(element).decode('utf-8'))
                if val != -1:
                    sum += val
                    data_amount += 1
            if data_amount != 0:
                average = sum/data_amount
                self.database.insert_sensor_record(i+1,average)
            
    def ppmConvert(self, val):
        if val != 0:
                ppm_val = val * 5 / 1024
                ppm_val = pow(10, (ppm_val-2.99)) - 0.2
                ppm_val = round(ppm_val, 2)
                if ppm_val <= 0:
                    ppm_val = 0.01

        else:
            ppm_val = 0
        return ppm_val
    #creates a label for sensor with the sensornumber given(num)
    def createSen(self, num):
        names = self.reader.tablesInit()
        names.pop(0)
        if len(names) >= num:
            return html.Th(names[num-1], style={'textAlign': 'center'})
        return html.Th("Szenzor {}".format(num), style={'textAlign': 'center'})
    #creates a button for the sensors with a number on it
    def createButton(self, id):
        button = dbc.Button(str(id) + " ppm", id = "SenBtnID "+str(id),style = 
            {"backgroundColor":"#00ff80", "color": "#000000", 'marginTop': '1%'})
        return button
    #creates a table with buttons and labels for the sensors
    def createTable(self):
        tempBtnIDS = []
        rows = []
        colnum = math.ceil(self.sensornumber/10)
        for i in range(0, 10):
            row = html.Tr(children = [])
            for j in range(0, colnum):
                current = j*10+i+1
                if current <= self.sensornumber:
                    row.children.append(self.createSen(current))
                    row.children.append(self.createButton(current))
                    tempBtnIDS.append("SenBtnID "+str(current))
            if row:
                rows.append(row)
        self.BtnIDS = tuple(tempBtnIDS)
        table_body = [html.Tbody(rows)]

        table = dbc.Table(table_body, bordered = False)
        return table
    #creates an interval component for updating the ammonia value
    def createInterval(self):
        interval = dcc.Interval(
            id = "interval-component",
            interval=100, # in milliseconds
            n_intervals=0,

        )
        return interval
    #update ppm values (currently called every second)
    def updating(self):
        self.lock.acquire()
        s = self.COMPORT.query()
        # print('released')
        self.lock.release()
        time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        #format example: sensor_1:2021-04-12-23-59-59 ==> 120 ppm
        self.redis_client.set("sensor_"+str(s.number)+":"+time, s.value, timedelta(minutes = 5))
        canbus = str(s.can)
        self.redis_client.set("canaddr_" + canbus, int(canbus), timedelta(minutes = 5))

    #creates a gauge graph
    def createGraph(self, number):
        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = number,
            mode = "gauge+number+delta",
            title = {'text': "Ammonia"},
            delta = {'reference': 50},
            gauge = {'axis': {'range': [None, 100], 'tickcolor': "white"},
                    'bordercolor': "grey",
                    'bar': {'color': "lightgreen"},
                    'steps' : [
                        {'range': [0, 20], 'color': "green"},
                        {'range': [20, 50], 'color': "yellow"},
                        {'range': [50, 100], 'color': "red"}],
                    'threshold' : {'line': {'color': "grey", 'width': 4}, 'thickness': 0.75, 'value': number}}))
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=30),
            width=500,
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            font = {'color': "white", 'family': "Arial"},
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    #creates a popup modal to show graphs and other sensor related data
    def createModal(self):
        mod = dbc.Modal(
            [
                dbc.ModalBody(
                    [
                        dbc.Button("KÜRT : ON", style={"float": "right"}, 
                            className="btn btn-outline-success", id = self.hornid, n_clicks=0),
                        dcc.Graph(id='graph-id', style={'marginLeft': '20%'}, config= {'displayModeBar': False}),
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id = self.closeid, className="ml-auto"
                    )
                ),
            ],
            id=self.modalid,
            style={"maxWidth": "none", "width": "50%"},
            is_open=False,
        )

        return mod
    #Combines the Table, Interval and Modal into one Div
    def mergeTable(self):
        mod = self.createModal()
        table = self.createTable()
        inter = self.createInterval()
        hidden = html.Div(id="hidden-div", style={'display':'none'})
        hidden2 = html.Div(id="hidden-div2", style={'display':'none'})
        audio = html.Audio(id = 'audio', src='/assets/beep.mp3', loop = True, controls = False)

        layout = html.Div([
            table,
            mod,
            inter,
            hidden,
            hidden2,
            audio
        ])
        self.layout = layout

    def call_callbacks(self):
        self.ButtonClickedCallback()
        self.JStoPython()
        self.buttonchange()

    #callback function for buttons (makes the modal visible/invisible)
    def ButtonClickedCallback(self):
        self.app.callback(
            Output(self.modalid, "is_open"),
            Output(self.hornid,"className"),
            Output(self.hornid, "children"),
            Output("graph-id", "figure"),
            [Input(i, "n_clicks") for i in self.BtnIDS],
            Input(self.hornid,"n_clicks"),
            Input(self.closeid,'n_clicks'),
            [State(self.modalid, "is_open")],
        )(self.ButtonClicked)
    #actual function for the buttons for closing and opening modals
    def ButtonClicked(self, *vals):
        ctx = dash.callback_context
        on = ["btn btn-outline-success", "KÜRT : ON"]
        off = ["btn btn-outline-danger", "KÜRT : OFF"]
        is_open = ctx.states['table-modal.is_open']
        if not ctx.triggered:
            button_id = 'No clicks yet'
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        found = button_id.find("SenBtnID")
        if (found != -1):
            self.currentSensor = button_id
        
        id = int(self.currentSensor.split(' ')[1])
        element = self.database.GetElementByID(id)
        if (button_id == self.hornid): #horn was clicked
            if element[0][2]: #if horn is true(horn is on)
                self.database.updateHorn(id, False)
                return dash.no_update, off[0], off[1], dash.no_update
            else: #if horn is off
                self.database.updateHorn(id, True)
                return dash.no_update, on[0], on[1], dash.no_update

        else : #btn was clicked
            data = self.redis_client.keys("*"+"sensor_"+str(id)+":"+"*")
            data.sort(reverse=True)
            ammonia_val = int(self.redis_client.get(data[0]).decode('utf-8'))
            ppm_val = self.ppmConvert(ammonia_val)
            fig = self.createGraph(ppm_val) 
            if element[0][2]: #if horn is on
                return not is_open, on[0], on[1], fig
            else: #if horn is off
                return not is_open, off[0], off[1], fig
    def JStoPython(self):
        self.app.server.route('/JSPY', methods = ['POST'])(self.DictToJSON)
    def DictToJSON(self):
        dict = {'num' : self.sensornumber}
        elements = self.database.getTheFirstX(self.sensornumber)
        for i in range(self.sensornumber):
            data = self.redis_client.keys("*"+"sensor_"+str(i+1)+":"+"*")
            if not data:
                dict.update({i+1 : {'color' : 'grey', 'ammonia' : 0}})
            else:
                data.sort(reverse=True)
                value = int(self.redis_client.get(data[0]).decode('utf-8'))
                ppm_val = self.ppmConvert(value)
                ppm_val = str(ppm_val) + ", "+ str(value)
                if not elements[i][2]:
                    dict.update({i+1 : {'color' : 'blue', 'ammonia' : ppm_val}})
                else:
                    if ppm_val == 0:
                        dict.update({i+1 : {'color' : 'grey', 'ammonia' : ppm_val}})
                    elif True:
                        dict.update({i+1 : {'color' : 'green', 'ammonia' : ppm_val}})
                    elif False:
                        dict.update({i+1 : {'color' : 'yellow', 'ammonia' : ppm_val}})
                    elif False:
                        dict.update({i+1 : {'color' : 'red', 'ammonia' : ppm_val}})
        return json.dumps(dict)
    def buttonchange(self):
        self.app.clientside_callback(
        """
        function a(interval) {
            if(interval > 0){
                postData();
                return 'Hello Dash1';
            }
            else{
                return 'Hello Dash2';
            }
        }
        function postData() {
            $.ajax({
                type: "POST",
                url: "/JSPY",
                dataType : "json",
                success: callbackFunc
            });
        }

        function callbackFunc(response) {
            //console.log(response)
            var arr = [];
            var hasRed = false;
            for (let i = 0; i < response['num']; i++) {
                color = response[i+1]['color']
                value = response[i+1]['ammonia']
                str = 'SenBtnID '.concat((i+1).toString())
                valstr = (value.toString()).concat(' ppm')
                document.getElementById(str).innerHTML = valstr
                if (color.localeCompare('green') == 0){
                    document.getElementById(str).style.background="#00ff80"
                }
                else if (color.localeCompare('red') == 0){
                    hasRed = true;
                    document.getElementById(str).style.background=color
                }
                else if (color.localeCompare('yellow') == 0){
                    hasRed = true;
                    document.getElementById(str).style.background=color
                }
                else {
                    document.getElementById(str).style.background=color
                }
            }
            if(hasRed){
                document.getElementById('audio').play();
            }
            else{
                document.getElementById('audio').pause();
            }
            // do something with the response
            //console.log('callbackFunc')
        }
        """,
        Output('hidden-div2', 'children'),
        Input("interval-component", "n_intervals"),
        Input('tabs', 'value')
        )

