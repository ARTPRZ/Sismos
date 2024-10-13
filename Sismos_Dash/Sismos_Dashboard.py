from dash import Dash, dcc, html, Input, Output
import numpy as np
import plotly.express as px
import pandas as pd
from plotly import graph_objs as go
from plotly.graph_objs import *
import dash_bootstrap_components as dbc
import datetime as dt

#Este es un testo para ver si se actualizo!!!   

#https://dash.gallery/ddk-oil-and-gas-demo/
#https://dash.gallery/dash-uber-rides-demo/
#https://dash-example-index.herokuapp.com/
#https://github.com/plotly/dash-sample-apps/blob/main/apps/dash-uber-rides-demo/app.py


#Create Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE],meta_tags=[{"name": "viewport", "content": "width=device-width"}])
app.title = "Sismos de Mexico"

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Columna para los controles del usuario (parte superior izquierda)
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Div(style={"height": "130px"}),
                        html.H2("Red Sísmica de México"),
                        html.Br(),
                        html.P(
                            """Selecciona una Magnitud:"""
                        ),

                        # Slider para seleccionar el rango de magnitudes (de 0.5 en 0.5)
                        dcc.RangeSlider(
                            id="magnitude-slider",
                            min=0.5,
                            max=8.5,
                            step=0.5,
                            marks={i: str(i) for i in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6,6.5,7,7.5,8,8.5]},
                            value=[5.5, 8.5],  # Rango inicial completo       
                        ),

                        html.Div(),
                         html.P(
                            """Selecciona el Año:"""
                        ),

                        # Slider para seleccionar el rango de fechas (años)
                        dcc.RangeSlider(
                            id="year-slider",
                            min=1985,
                            max=2024,
                            step=1,
                            marks={year: str(year) for year in range(1985, 2025, 5)},  # Intervalos de 5 años
                            value=[1985, 2024]  # Rango inicial completo
                        ),

                        html.Div(style={"height": "5px"}),
                        html.P(id="total-sismos"),
                        html.P('Actualizado al: VAMOS A VER AHORA'),
                        dcc.Markdown(
                            """
                            Source: [Sismológico Nacional](http://www2.ssn.unam.mx:8080/catalogo/) 
                            """
                        ),


                    ],
                ),
       
                # Columna para el mapa (ocupando todo el lado derecho)
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph", style={"height": "98vh"},config={ 'scrollZoom': True}),  # Mapa ocupando todo el espacio derecho
                    ],
                ),
            ],
        )
    ]
)


# Dictionary of important locations in New York
list_of_locations = {
    "Pinotepa Nacional": {"lat": 16.338055555556, "lon": -98.050277777778},
    "Central Nuclear Laguna Verde ": {"lat": 19.72078333, "lon": -96.40634167},
    "Zócalo CDMX": {"lat":  19.4326018, "lon": -99.1332049},
    "Ángel de la Independencia": {"lat": 19.4269903, "lon":  -99.1676463 },
    "Alameda del sur": {"lat": 19.309114, "lon":  -99.122794},
    "Volcán Popocatépetl": {"lat": 19.02222, "lon": -98.62778},
}

#Initialize data frame
#Read data--------------------------------------------
# Lista de archivos que quieres unir
files = ['BD_Sismos/sismo_0.csv', 'BD_Sismos/sismo_1.csv', 'BD_Sismos/sismo_2.csv', 'BD_Sismos/sismo_3.csv', 'BD_Sismos/sismo_4.csv']

# Leer cada archivo CSV y unirlos
df_list = [pd.read_csv(file) for file in files]

# Concatenar todos los DataFrames
df_combined = pd.concat(df_list, ignore_index=True)

sns=df_combined


sns2 = sns[sns.Magnitud.notna()]
sns2 = sns2[sns2.Magnitud != 'no calculable']
sns2.Magnitud = pd.to_numeric(sns2.Magnitud)
sns2.Fecha = pd.to_datetime(sns2.Fecha,format ="%Y-%m-%d")
df = sns2[sns2.Fecha >= dt.datetime(1985,1,1)]
df['Año'] = df['Fecha'].dt.year



# Temp Dropdown Values----------------------------------------
dropdown_values = {
    'regions':['APLT','APAPCH','IDK']
}



# Callback para actualizar el gráfico de mapa basado en los sliders de magnitud y años
@app.callback(
    Output("map-graph", "figure"),
    [Input("magnitude-slider", "value"),
     Input("year-slider", "value")]
)
def update_map(magnitude_range, year_range):
    # Filtrar los datos con base en los valores de los sliders
    filtered_df = df[
        (df['Magnitud'] >= magnitude_range[0]) & 
        (df['Magnitud'] <= magnitude_range[1]) &
        (df['Año'] >= year_range[0]) &
        (df['Año'] <= year_range[1])
    ]

    # Crear el mapa con los datos filtrados
    figure1 = go.Figure(
        data=[
            go.Scattermapbox(
                lat=filtered_df['Latitud'],  # Reemplaza con la columna de latitud de tu DataFrame
                lon=filtered_df['Longitud'],  # Reemplaza con la columna de longitud de tu DataFrame
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=filtered_df['Magnitud'] * 2,  # Tamaño proporcional a la magnitud
                    color=filtered_df['Magnitud'],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(
                        title="Magnitud",
                        x=0.93,
                        xpad=0,
                        nticks=20,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                        outlinewidth=0
                    ),
                ),


                
                text=filtered_df['Fecha'].astype(str) + '<br>' + 'Magnitud: ' + filtered_df['Magnitud'].astype(str),
                hoverinfo="text"
            ),
 # Añadir las ubicaciones importantes del diccionario `list_of_locations`
            go.Scattermapbox(
                lat=[loc["lat"] for loc in list_of_locations.values()],  # Extraer latitudes
                lon=[loc["lon"] for loc in list_of_locations.values()],  # Extraer longitudes
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=10,
                    color='#FFA0A0',  # Color azul para las ubicaciones
                ),
                text=list(list_of_locations.keys()),  # Mostrar el nombre de la ubicación en el hover
                hoverinfo="text",
                name="Ubicaciones importantes"
            )

        ],
        layout=go.Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=0, t=0, b=0),
            mapbox=dict(
                accesstoken= mapbox_access_token,  # Reemplaza con tu token de Mapbox
                center=dict(lat=23, lon=-102),
                zoom=4.8,  # Ajusta el zoom según tus necesidades
                style="carto-darkmatter",
            ),
             showlegend=False,
             uirevision='map'  # Preserva el estado de la interfaz de usuario
        )
    )

    return figure1


# Callback para actualizar el total de sismos basado en el rango de magnitud y el año
@app.callback(
    Output("total-sismos", "children"),
    [Input("magnitude-slider", "value"), Input("year-slider", "value")]
)
def update_total_sismos(magnitude_range, year_range):
    # Filtrar los datos según el rango de magnitud y el año seleccionado
    # Filtrar los datos con base en los valores de los sliders
    filtered_df = df[
        (df['Magnitud'] >= magnitude_range[0]) & 
        (df['Magnitud'] <= magnitude_range[1]) &
        (df['Año'] >= year_range[0]) &
        (df['Año'] <= year_range[1])
    ]

    # Contar el total de sismos en el rango seleccionado
    total_sismos = len(filtered_df)

    # Mostrar el total
    return "Total de sismos: {:,d}".format(total_sismos)


 
#Run app
if __name__ == '__main__':
    app.run_server(debug=True)

        
