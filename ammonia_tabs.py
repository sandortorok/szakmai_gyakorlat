import dash
from dash import html
from dash import dcc
import ammonia_records as R
import ammonia_tables as tt
import ammonia_controlPanel as cp
import ammonia_canbusAddresses as can

app = dash.Dash(__name__)

recordstab = R.RecordTab(app)
tabletab = tt.tablesTab(app)
roomstab = cp.RoomsTab(app)
cantab = can.canAddr(app)

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-4',colors={'border': '#00ff80'}, children=[
        dcc.Tab(label='Tab one',selected_className="text-light", selected_style={"backgroundColor" : "#222222"},
            style = {"backgroundColor" : "#222222"}, className="text-light",value='tab-1', children= 
            [
                recordstab.layout
            ]
        ),
        dcc.Tab(label='Tab two',selected_className="text-light", selected_style={"backgroundColor" : "#222222"},
            style = {"backgroundColor" : "#222222"}, className="text-light", value='tab-2', children=
            [
                tabletab.layout
            ],
        ),
        dcc.Tab(label='Tab three',selected_className="text-light", selected_style={"backgroundColor" : "#222222"},
            style = {"backgroundColor" : "#222222"}, className="text-light", value='tab-3', children=
            [
                roomstab.layout
            ]
        ),
        dcc.Tab(label='Tab four',selected_className="text-light", selected_style={"backgroundColor" : "#222222"},
            style = {"backgroundColor" : "#222222"}, className="text-light", value='tab-4', children=
            [
                cantab.layout
            ]
        ),
    ]),
])


server = app.server
