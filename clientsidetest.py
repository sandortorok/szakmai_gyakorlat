
from os import truncate
from dash.resources import Scripts
import dash_bootstrap_components as dbc
import dash
from dash_bootstrap_components._components.Button import Button
import dash_core_components as dcc
from dash_core_components.Store import Store
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import COM
import logging
import threading
import dash_defer_js_import as dji
import json
import random

class clientside:
    def __init__(self):
        self.btnIDS = []
    def createSen(self, num):
        return html.Th("Szenzor {}".format(num))
    def createButton(self, id):
        button = dbc.Button(str(id), id = "SenBtnID "+str(id),style = 
            {"marginLeft" : "10%", "marginTop": "10%", "backgroundColor":"#00ff80", "color": "#000000"})
        return button
    def createTable(self):
        tempBtnIDS = []
        rows = []
        for i in range(0, 15):
            row = html.Tr(children = [])
            for j in range(0, 8):
                current = i*8+j+1
                row.children.append(self.createSen(current))
                row.children.append(self.createButton(current))
                tempBtnIDS.append("SenBtnID "+str(current))
            rows.append(row)
        self.btnIDS = tuple(tempBtnIDS)
        table_body = [html.Tbody(rows)]

        table = dbc.Table(table_body, bordered = False)
        return table

external_scripts2 = ['https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js']

cl = clientside()
app = dash.Dash(__name__, external_scripts=external_scripts2)
app._favicon = (app.get_asset_url('favicon.ico'))
app.layout = html.Div(children=[
    html.H1(children='Hello Dash', id = 'hello'),
    dbc.Button('BUTTON', id = 'testinput', n_clicks= 0),
    html.Div(children='''
        Dash: A web application framework for Python.
    ''', id = 'testdiv'),
    dcc.Interval(id = 'storing_interval', n_intervals=0, interval=100),
    html.Audio(id = 'audio', src=app.get_asset_url('furelise.mp3'), autoPlay= True, loop = True, controls = False),
    html.Article(dji.Import(src=app.get_asset_url('test_javascript.js'))),
    cl.createTable()
])

globalvar = 0

def printfunction():
    dict = {}
    global globalvar
    globalvar += 20
    for i in range(15*8):
        x = (globalvar + i) * 3 % 255
        dict.update({(i+1) : x})
    return json.dumps(dict)
app.server.route('/func', methods = ['POST'])(printfunction)



app.clientside_callback(
    """
    function a(interval) {
        if(interval > 0){
            postData()
            return 'Hello Dash1';
        }
        else{
            return 'Hello Dash2';
        }
    }
    function postData() {
        //console.log('postData')
        $.ajax({
            type: "POST",
            url: "/func",
            dataType : "json",
            success: callbackFunc
        });
    }

    function callbackFunc(response) {
        var arr = [];
        for (let i = 0; i < 15*8; i++) {
            x = response[i+1]
            str = 'SenBtnID '.concat((i+1).toString())
            document.getElementById(str).innerHTML = x
            color = "rgba(".concat("0,",x.toString(),",",x.toString(),",0.6)")
            document.getElementById(str).style.background=color
        }
        // do something with the response
        //console.log('callbackFunc')
    }

    """,
    Output('hello', 'children'),
    Input('storing_interval', 'n_intervals')
    )
app.clientside_callback(
    '''
    function asd(clicks) {
        if(clicks > 0){
            document.getElementById('audio').play();
            if ("serial" in navigator) {
                console.log('serial')
                const port = navigator.serial.requestPort();
                ports = navigator.serial.getPorts();
                console.log(ports);
            }
        }
        return document.getElementById('testdiv').innerHTML
    }
    ''',
    Output('testdiv', 'children'),
    Input('testinput', 'n_clicks')
)

if __name__ == '__main__':

    app.run_server(debug=True)