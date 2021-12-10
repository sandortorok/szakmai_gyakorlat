import dash_bootstrap_components as dbc
import dash_html_components as html
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = [dbc.themes.BOOTSTRAP]

def create_card(SensNum,ppm):
    return dbc.Card(
        dbc.CardHeader("Szenzor {}".format(SensNum)),
        dbc.CardBody(
            [
                html.H5("{} [ppm]".format(ppm), className="card-title"),
                dbc.Button(
                    "info", color="dark", className="mt-auto"
                ),
            ]
        )
    )

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
card_content = [
    dbc.CardHeader("Card header"),
    dbc.CardBody(
        [
            html.H5("Card title"),
            dbc.Button("info", color="light"),
        ]
    ),
]

coloured_cards = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),

            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
            ]
        ),
    ]
)
app.layout = coloured_cards

if __name__ == "__main__":
    app.run_server()