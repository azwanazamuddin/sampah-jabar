from re import M
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import pickle

main_data = pd.read_excel('main_data.xlsx')
main_data['tahun'] = main_data['tahun'].apply(str)
#main_data = main_data.groupby(['nama_kabupaten_kota','tahun'])['volume_produksi'].agg('sum').reset_index(name = 'Total Volume (liter/hari)')

# Loading model
model_file = open('model.pkl', 'rb')
model = pickle.load(model_file, encoding='bytes')

# Create the line graph
bar_graph = px.bar(
  # Set the appropriate DataFrame and title
  data_frame=main_data, 
  x='nama_kabupaten_kota', y='VP',
  color='tahun',
  barmode='group',
  labels = dict(
      nama_kabupaten_kota='Kabupaten/Kota',
      VP='Volume Produksi Sampah (liter/hari)',
      tahun='Tahun'
  ))

utama = html.Div(
    children=[
        # Add a H1
        html.H1("Total Volume Produksi Sampah Jawa Barat setiap Tahun"),
        # Add both graph
        dcc.Graph(id='bar_graph', figure=bar_graph),
        html.Div(id='output-prediksi')
])

# Create the Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Prediksi Sampah Jabar", className="display-5"),
        html.Hr(),
        html.P(
            "Prediksi volume sampah per hari Kabupaten/Kota di Jawa Barat", className="lead"
        ),
        html.Div(
            [
                dbc.Label("Populasi", html_for="populasi"),
                dbc.Input(type="number", id="populasi", placeholder="Jumlah Populasi (jiwa)"),
            ],
        className="mb-3"
        ),
        html.Div(
            [
                dbc.Label("Pengeluaran per Kapita", html_for="out_capita"),
                dbc.Input(type="number", id="out_capita", placeholder="Pengeluaran (Rupiah)"),
            ],
        className="mb-3"
        ),
        html.Div(
            [
                dbc.Label("Indeks Pendidikan", html_for="ipend"),
                dbc.Input(type="number", id="ipend", placeholder="Indeks Pendidikan"),
            ],
        className="mb-3"
        ),
        html.Div(
            [
                dbc.Label("Indeks Pengeluaran", html_for="ipeng"),
                dbc.Input(type="number", id="ipeng", placeholder="Indeks Pengeluaran"),
            ],
        className="mb-3"
        ),
        html.Div(
            dbc.Button("Prediksi!", id="submit", color="success", className="me-1", n_clicks=0)
        )
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output("output-prediksi", "children"),
    Input("submit","n_clicks"),
    State("populasi", "value"),
    State('out_capita', 'value'),
    State('ipend', 'value'),
    State('ipeng', 'value'))
def prediksi(n_clicks, populasi, out_capitas, ipend, ipeng):
    data = []

    data.append(np.log(float(populasi)))
    data.append(np.log(float(out_capitas)))
    data.append(np.log(float(ipend)))
    data.append(np.log(float(ipeng)))

    prediction = model.predict([data])
    hasil = np.round(np.exp(prediction[0]), 2)
    print(hasil)
    return "Prediski: {} liter/hari".format(hasil)

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return utama
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

if __name__ == '__main__':
    app.run_server(debug=True)