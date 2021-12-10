import dash
from dash_bootstrap_components.themes import BOOTSTRAP
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import ammonia_reader as am_r
class RoomsTab:
    def __init__(self, app):
        self.service = False
        self.buttonIDS = ('green-1', 'green-2', 'green-3', 'green-4', 'red-1', 'red-2', 'red-3', 'red-4', 'horn-1', 'horn-2')
        reader = am_r.Read()
        self.elements = reader.controlPanelInit()
        #starting values
        self.serviceIDS = ('input', 'submit', 'remove', 'add-green', 'add-red', 'add-horn',
            'remove-green', 'remove-red', 'remove-horn')
        self.app = app
        self.createLayout()
        self.Dropdown()
        self.DisableButtons()
        self.OnOffButton()
        self.ModalToggle()
        self.PasswordCheck()
    def createGreenButton(self, id):
        button = dbc.Button(
            id = id,
            disabled=False,
            children=
                [
                    html.Img(src=self.app.get_asset_url('2.png'), style={'height':'100%', 'width':'100%'})
                ],
            style = {'borderColor': '#222222', 'backgroundColor': '#222222',
                'height': '8%', 'width' : '8%','marginRight' : '5%', 'marginLeft' : '5%'}, 
            )
        return button
    def createRedButton(self, id):
        button = dbc.Button(
            id = id,
            children=
                [
                    html.Img(src=self.app.get_asset_url('1.png'), style={'height':'100%', 'width':'100%'})
                ],
            style = {'borderColor': '#222222', 'backgroundColor': '#222222',
                'height': '8%', 'width' : '8%','marginRight' : '5%', 'marginLeft' : '5%'})
        return button
    def createHornButton(self, id):
        button = dbc.Button(
            id = id,
            children=
                [
                    html.Img(src=self.app.get_asset_url('3.png'), style={'height':'100%', 'width':'100%'})
                ],
            style = {'borderColor': '#222222', 'backgroundColor': '#222222',
                'height': '8%', 'width' : '8%','marginRight' : '10%', 'marginLeft' : '10%'})
        return button
    def createModal(self):
        modal = dbc.Modal(
            [
                dbc.ModalHeader("Service Mode"),
                dbc.ModalBody([
                    "Password: ",
                    dbc.Input(
                        id='password-input', 
                        type = "password", 
                        value='', 
                        className="mr-1",
                        style={'marginTop' : '2%'}),
                    dbc.Button("Enter", 
                        id="password-submit", 
                        className="ml-auto", 
                        n_clicks=0,
                        style={'marginTop' : '2%','float': 'right'},
                        color= 'primary'
                    )
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="password-close", className="ml-auto", n_clicks=0, color= 'primary')
                ),
            ],
            id="password-modal",
            size="xl",
            is_open=False,
            )
        return modal
    def createLayout(self):
        self.layout = html.Div([
            self.createServiceButtons(),
            dcc.Dropdown(
                options= self.AddInitialElements(),
                value = self.elements[0]['id'],
                clearable = False,
                className="dash-bootstrap",
                id = 'dropdown-2',
                style={ 'width': '150px'},

            ),
            html.Div(children = [
                self.createGreenButton('green-1'),
                self.createGreenButton('green-2'),
                self.createRedButton('red-1'),
                self.createRedButton('red-2'),
            ], 
            style={'display': 'inline-block', 'textAlign': 'center', 'marginTop': '2%'}),

            html.Div(children = [
                self.createGreenButton('green-3'),
                self.createGreenButton('green-4'),
                self.createRedButton('red-3'),
                self.createRedButton('red-4'),
            ], 
            style={'display': 'inline-block', 'textAlign': 'center', 'marginTop': '2%'}),
            html.Div(children = [
                self.createHornButton('horn-1'),
                self.createHornButton('horn-2'),
            ], 
            style={'display': 'inline-block', 'textAlign': 'center', 'marginTop': '2%'}),
            dbc.Button('Service Mode', id='service', className="glow-on-hover",
            style = {'position': 'absolute', 'left' : 50, 'bottom' : 50}),
            self.createModal(),

        ])
    def createServiceButtons(self):
        div = html.Div([
            dbc.Input(id='input', type = "text", value='', className="mr-1"),
            dbc.Button('Add Option', id='submit', className="glow-on-hover"),
            dbc.Button('Remove Option', id = 'remove', className="glow-on-hover"),
            dbc.Button('Add Green', id='add-green', className="glow-on-hover"),
            dbc.Button('Add Red', id='add-red', className="glow-on-hover"),
            dbc.Button('Add Horn', id='add-horn', className="glow-on-hover"),
            dbc.Button('Remove Green', id='remove-green', className="glow-on-hover"),
            dbc.Button('Remove Red', id='remove-red', className="glow-on-hover"),
            dbc.Button('Remove Horn', id='remove-horn', className="glow-on-hover"),
        ])
        return div
    def AddInitialElements(self):
        array = []
        for e in self.elements:
            array.append({'label' : e['id'], 'value' : e['id']})
        return array
    def removeElementFromDict(self, id):
        for button in self.elements:
            if button['id'].lower() == id.lower():
                self.elements.remove(button)
    def Dropdown(self):
        self.app.callback(
            Output('dropdown-2', 'options'),
            [Input('submit', 'n_clicks'), Input("remove", "n_clicks")],
            [State('input', 'value'), State('dropdown-2', 'options')],
        )(self.DropdownCallback)
    def DropdownCallback(self, submit, remove, new_value, current_options):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_options
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == "submit":
            for item in current_options:
                if item['label'].lower() == new_value.lower(): #már van ilyen nevű, .lower() a case sensitivity miatt
                    return current_options
            current_options.append({'label': new_value, 'value' : new_value})
            vals = (True, True, True, True, True, True, True, True, True, True, True, True)
            dict1 = dict(zip(self.buttonIDS, vals))
            self.elements.append({'id' : new_value, 'green' : 2, 'red' :  2, 'horn' : 2}| dict1)
            return current_options

        elif button_id == "remove":
            for item in current_options:
                if item['label'].lower() == new_value.lower():
                    current_options.remove(item)
                    self.removeElementFromDict(new_value)
                    return current_options
        return current_options
    def DisableButtons(self):
        self.app.callback(
            [Output(btn, 'disabled') for btn in self.buttonIDS],
            [Input(btn, "n_clicks") for btn in ['add-green', 'add-red', 'add-horn', 'remove-green', 'remove-red', 'remove-horn']],
            Input('dropdown-2', 'value')
        )(self.DisableButtonscallback)
    def DisableButtonscallback(self, *vals):
        ctx = dash.callback_context
        # print(ctx.triggered[0]['prop_id'].split('.')[0])
        # if not ctx.triggered:
        #     raise PreventUpdate
        # else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        dropdown_value = vals[len(vals)-1]
        if button_id != "dropdown-2" and button_id != "":
            action,color = button_id.split('-')
            if action == 'add':
                for e in self.elements: 
                    if e['id'] == dropdown_value:
                        if color == 'horn':
                            if e[color] < 2:
                                e[color] += 1
                        else:
                            if e[color] < 4:
                                e[color] += 1
            elif action == 'remove':
                for e in self.elements: 
                    if e['id'] == dropdown_value:
                        if e[color] > 0:
                            e[color] -= 1

        array = []
        for e in self.elements:
            if e['id'] == dropdown_value:
                for type in ['green', 'red', 'horn']:
                    for i in  range(e[type]):
                        array.append(False)
                    if type == 'horn':
                        for i in range(2-e[type]):
                            array.append(True)
                    else:
                        for i in range(4-e[type]):
                            array.append(True)
                return array
    def OnOffButton(self):
        for btn in self.buttonIDS:
            self.app.callback(
                Output(btn, 'children'),
                [Input(btn, 'n_clicks'),Input('dropdown-2', 'value')]
            )(self.OnOffButtonCallback)
    def OnOffButtonCallback(self, click, val):
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            swap = False
            if button_id == 'dropdown-2':
                swap = True
                button_id = (list(ctx.inputs.keys()))[0].split('.')[0]
            b_color = button_id.split('-')[0]
            colors = ['green', 'red', 'horn']
            numbers = [2, 1, 3]
            for color, number in zip(colors,numbers):
                if b_color == color:
                    for e in self.elements:
                        if e['id'] == val:
                            if not swap:
                                e[button_id] = not e[button_id]
                                if not e[button_id]:
                                    return html.Img(src=self.app.get_asset_url(str(number) + '_sotet.png'), style={'height':'100%', 'width':'100%'})
                                else:
                                    return html.Img(src=self.app.get_asset_url(str(number) + '.png'), style={'height':'100%', 'width':'100%'})
                            elif e[button_id]:
                                return html.Img(src=self.app.get_asset_url(str(number) + '.png'), style={'height':'100%', 'width':'100%'})
                            else:
                                return html.Img(src=self.app.get_asset_url(str(number) + '_sotet.png'), style={'height':'100%', 'width':'100%'})
        raise PreventUpdate
    def ModalToggle(self):
        self.app.callback(
            Output('password-modal', 'is_open'),
            [Input('service', 'n_clicks'), Input('password-close', 'n_clicks')],
            [State('password-modal', 'is_open')]
        )(self.ModalToggleCallback)
    def ModalToggleCallback(self, n1, n2, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if not self.service and button_id == 'service':
            return not is_open
        if button_id == 'password-close':
            return not is_open
        return is_open
    def PasswordCheck(self):
        self.app.callback(
            [Output(services,'style') for services in self.serviceIDS],
            Output('password-input', 'value'),
            [Input('password-submit', 'n_clicks'), Input('service', 'n_clicks')],
            State('password-input', 'value')
        )(self.PasswordCheckCallback)
    def PasswordCheckCallback(self, submit, service,  input):
        ctx = dash.callback_context

        hidden = []
        for o in self.serviceIDS:
            hidden.append({'visibility' : 'hidden'})
        hidden.append("")
        visible = []
        for o in self.serviceIDS:
            visible.append({'visibility' : 'visible'})
        visible.append("")

        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        else:
            if self.service:
                return visible
            elif not self.service:
                return hidden

        if button_id == 'service':
            if self.service:
                self.service = False
                return hidden
            else:
                raise PreventUpdate
        if button_id == 'password-submit':
            if input == 'sakkiraly11':
                self.service = True
                return visible
            else:
                raise PreventUpdate
if __name__ == "__main__":
    app = dash.Dash(__name__)
    rt = RoomsTab(app)
    app.layout = rt.layout
    app.run_server()