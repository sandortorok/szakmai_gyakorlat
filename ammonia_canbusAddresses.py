import redis
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


class canAddr:
    def __init__(self, app):
        self.app = app
        self.service = False
        self.redis_client = redis.Redis(host='localhost', port='6379')
        self.layoutMaker()
        self.changeListCallback()
        self.ModalToggle()
        self.Passwordcheck()
    def createModal(self):
        modal = dbc.Modal(
            [
                dbc.ModalHeader("Log In", id = 'can-header'),
                dbc.ModalBody([
                    "Password: ",
                    dbc.Input(
                        id='can-password-input', 
                        type = "password", 
                        value='', 
                        className="mr-1",
                        style={'marginTop' : '2%'}),
                    dbc.Button("Enter", 
                        id="can-password-submit", 
                        className="ml-auto", 
                        n_clicks=0,
                        style={'marginTop' : '2%','float': 'right'},
                        color= 'primary'
                    )
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="can-password-close", className="ml-auto", n_clicks=0, color= 'primary')
                ),
            ],
            id="can-password-modal",
            size="xl",
            is_open=False,
            )
        return modal
    def layoutMaker(self):
        layout = html.Div(children =[
            dbc.Button("Reset", id = 'resetbtn'),
            self.createModal(),
            dcc.Interval(
                        id = "can-interval",
                        interval=1000, # in milliseconds
                        n_intervals=0,
            ),
            html.Div(
                [
                    dbc.ListGroup(
                        [
                        ],
                        horizontal = True,
                        className="mb-2 mt-2",
                    ),
                    dbc.ListGroup(
                        [
                        ],
                        horizontal = True,
                        className="mb-2 mt-2",
                    ),
                ],
                id = 'div-id'
            ),
            dbc.Button(
                'Service Mode ON', 
                id='can-service', 
                className="glow-on-hover",
                style = {'position': 'absolute', 'left' : 50, 'bottom' : 50}
            ),
        ])


        self.layout = layout
    def changeListCallback(self):
        self.app.callback(
            Output('div-id', 'children'),
            Input('resetbtn', 'n_clicks'),
            Input("can-interval","n_intervals"),
            Input('tabs', 'value'),
            State('div-id', 'children')
        )(self.changelist)
    def changelist(self, reset, interval, tab, div):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'No clicks yet'
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'tabs' or button_id == "can-interval":
            data = self.redis_client.keys("*canaddr_*")
            addrList = []
            divaddresses = []
            for i in data:
                addrList.append(int(self.redis_client.get(i).decode('utf-8')))
            addrList.sort()


            needchange = False
            for i in range(len(div)):
                for j in range(len(div[i]['props']['children'])):
                    divname = div[i]['props']['children'][j]['props']['children']
                    divnum = divname.split(" ")[-1]
                    divaddresses.append(int(divnum))
            if set(addrList) != set(divaddresses):
                needchange = True
            if self.service == False:
                #reseting
                for i in range(len(div)):
                    div[i]['props']['children'].clear()
                addresses = self.redis_client.keys("*canaddr_*")
                for i in addresses:
                    self.redis_client.delete(i)
                return div

            if needchange:
                for i in range(len(div)):
                    div[i]['props']['children'].clear()
                for i in addrList:
                    name = "CANBUS ADDRESS: " + str(i)
                    temp = {
                        "props": {
                            "children": name,
                            "style": {"backgroundColor": "#00ff80", "color": "#000000"},
                        },
                        "type": "ListGroupItem",
                        "namespace": "dash_bootstrap_components",
                    }
                    addable = False
                    added = False
                    for i in range(len(div)):
                        if len(div[i]['props']['children']) < 6:
                            addable = True
                        if addable and not added:
                            div[i]['props']['children'].append(temp)
                            added = True
                    if addable == False and added == False:
                        temp2 = {
                            "props": {"children": [], "className": "mb-2 mt-2", "horizontal": True},
                            "type": "ListGroup",
                            "namespace": "dash_bootstrap_components",
                        }
                        div.append(temp2)
                        div[-1]['props']['children'].append(temp)
                return div
            else:
                raise PreventUpdate

        elif button_id == 'resetbtn':
            #reseting
            for i in range(len(div)):
                div[i]['props']['children'].clear()
            addresses = self.redis_client.keys("*canaddr_*")
            for i in addresses:
                self.redis_client.delete(i)
        return div
    def ModalToggle(self):
        self.app.callback(
            Output('can-password-modal', 'is_open'), 
            Output('can-service', 'children'),
            Input('can-service', 'n_clicks'), 
            Input('can-password-close', 'n_clicks'),
            State('can-password-modal', 'is_open')
        )(self.ModalToggleCallback)
    def ModalToggleCallback(self, n1, n2, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if self.service and button_id == "can-service":
            self.service = False
            return [is_open, 'Service Mode ON']
        else:
            return [not is_open, 'Service Mode OFF']
    def Passwordcheck(self):
        self.app.callback(
            Output('can-password-input', 'value'),
            Input('can-password-submit', 'n_clicks'),
            State('can-password-input', 'value')
        )(self.PasswordCheckCallback)
    def PasswordCheckCallback(self, enter, input):
        if enter and input == 'sakkiraly11':
            self.service = True
        return ''
        






