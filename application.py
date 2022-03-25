import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
import pandas as pd
import os,json
import base64
import geopandas as gpd
import plotly.graph_objs as go
from plotly import tools
import plotly.express as px

mapbox_token = "pk.eyJ1IjoiYWRlYm95ZWEiLCJhIjoiY2wwaWpjcW0wMDM3azNibGdhbTRubXB3ayJ9.6UyFRoMwp6XytQwQua-9WA"
px.set_mapbox_access_token(mapbox_token)
os.chdir(os.getcwd())

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG], 
    assets_folder ="static",
    assets_url_path="static",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "UK Traffics Analytics"

server = app.server

df_uk_geojson_pq = gpd.read_parquet('data/uk_geojson_agg.parquet')
df_uk_lad_geojson_pq = gpd.read_parquet('data/uk_lad_geojson_agg.parquet')
df_uk_aadf_pq = pd.read_parquet('data/df_uk_aadf.parquet.gzip')

uk_traffic_volume = pd.read_csv("data/uk_traffic_volume.csv")
vehicle_traffic_volume = pd.read_csv("data/vehicle_traffic_volume.csv")
rd_category_agg = pd.read_csv("data/rd_category_agg.csv")
veh_rd_traffic_volume = pd.read_csv("data/veh_rd_traffic_volume.csv")
rd_type_traffic_volume = pd.read_csv("data/rd_type_traffic_volume.csv")

df_road_geojson = pd.read_csv("data/road_geojson.csv")
df_road_top10 = pd.read_csv("data/road10_geojson.csv")
df_road_top50 = pd.read_csv("data/road50_geojson.csv")
df_road_top100 = pd.read_csv("data/road100_geojson.csv")

uk_topofile = "data/con_map.geojson"
uk_lad_json = "data/uk_lad_new.geojson"

road_dict = {"All": df_road_geojson, "Top 10": df_road_top10, "Top 50": df_road_top50, "Top 100": df_road_top100}

with open(uk_topofile) as f:
    uk_data = json.load(f)
    
with open(uk_lad_json) as f:
    lad_data = json.load(f)
    
vehs = ["Heavy Goods Vehicles", "Motor vehicles", "All vehicles", "Buses and Coaches", "Cars and Taxis", "2 rigid axle HGV", 
        "3/4 rigid axle HGV", "3 rigid axle HGV", "4 rigid axle HGV", 
        "5 articulated axle HGV", "6 articulated axle HGV", "Lorries and Vans",
        "Pedal Cycles", "Motor Cycles"]
        
yrs = sorted([2019, 2018, 2020, 2014, 2017, 2015, 2016, 2011, 2001, 2009, 2010,
            2013, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2012, 2000])
            
regions = ["London", "South West", "East Midlands", "Scotland", "Wales", "North West",
           "East of England", "Yorkshire & Humber", "South East", "West Midlands",
           "North East"]

year_diff = [f"{yr}-{yr2}" for yr in range(2000,2021) for yr2 in range(yr+1,2021)]
year_marks = {x:{"label":f"{x}",} for x in range(2000,2021)}

image_filename = 'data/british-flag.png' #image path
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

logo = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height="30px")),
                        dbc.Col(dbc.NavbarBrand("UK Traffics", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler2", n_clicks=0),
            dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Maps", href="/maps")),
                dbc.NavItem(dbc.NavLink("Charts", href="/charts")),
            ],
            brand="Home",
            brand_href="/",
            sticky="top",
            color="dark",
            dark=True,
            expand="lg",
            className="ms-2"

        )
         
        ],
    ),
    color="dark",
    dark=True,
    className="mb-5",
)

CONTENT_STYLE = {
    "padding-top": "0rem",
    "margin-top": "0rem",
    "margin-left": "1rem",
    "margin-right": "1rem",
    "padding": "0rem 1rem",
}

content = html.Div(id="page-content", style=CONTENT_STYLE)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#060606",
    "margin-top": "5rem",
}

sidebar = html.Div(
    [
     dbc.Row(
         dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right',  "margin-left": "2.3rem"}, children='Select Vehicles:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0}),
     ),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '17px', 'width': '230px'},
                id='vehicle-dropdown',
                options=vehs,
                value=vehs[0],
                clearable=False),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
      html.Br(),
     dbc.Row(dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right', "margin-left": "1rem"}, children='Select Year:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':1}),),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '17px', 'width': '230px'},
                id='year-dropdown',
                options=yrs,
                value=yrs[0],
                clearable=False),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
      html.Br(),
     dbc.Row(dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right', "margin-left": "1rem"}, children='Select Regions:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':1})),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '16px', 'width': '230px'},
                id='region-dropdown',
                options=regions,
                value=regions[0],
                clearable=False),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
       dbc.Row(),
    ],
    style=SIDEBAR_STYLE,
)

SIDEBAR1_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#060606",
    "margin-top": "5rem",
}

sidebar_1 = html.Div(
    [
     dbc.Row(
         dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right',  "margin-left": "2.4rem"}, children='Select Vehicles:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0}),
     ),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '17px', 'width': '250px'},
                id='veh-dropdown',
                options=vehs,
                value=vehs[0],
                clearable=False),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
      html.Br(),
     dbc.Row(dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right', "margin-left": "1rem"}, children='Select Regions:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':1})),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '16px', 'width': '250px'},
                id='reg-dropdown',
                options=regions,
                multi=True,
                value=regions,
                clearable=False),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
     html.Br(),
     dbc.Row(dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right', "margin-left": "1rem"}, children='Select Year:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':1}),),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '17px', 'width': '250px'},
                id='yr-dropdown',
                options=yrs,
                value=yrs[0],
                clearable=False),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
     html.Br(),
     dbc.Row(dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right', "margin-left": "1rem"}, children='Select Diff. btw Year:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':1}),),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '17px', 'width': '250px'},
                id='year-diff-dropdown',
                options=year_diff,
                value=year_diff[-1],
                clearable=False),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
     html.Br(),
     html.Br(),
     html.Br(),
     
    ],
    style=SIDEBAR1_STYLE,
)

SIDEBAR2_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#060606",
    "margin-top": "15.6rem",
}

sidebar_2 = html.Div(
    [
     dbc.Row(
         dbc.Col(html.H6(style={'text-align': 'center', 'justify-self': 'right',  "margin-left": "2.3rem"}, children='Major Roads:'),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':3},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0}),
     ),
     dbc.Row(dbc.Col(dcc.Dropdown(
                style = {'text-align': 'center', 'font-size': '17px', 'width': '230px'},
                id='road-dropdown',
                options=['All', 'Top 10', 'Top 50', "Top 100"],
                value="All",
                clearable=False,
                placeholder="Select Roads"),
                xs={'size':'auto', 'offset':0}, sm={'size':'auto', 'offset':0}, md={'size':'auto', 'offset':0},
                lg={'size':'auto', 'offset':0}, xl={'size':'auto', 'offset':0})),
      html.Br()
    ],
    style=SIDEBAR2_STYLE,
)

yearSlider = html.Div([
    dbc.Row(dbc.Col(dcc.RangeSlider(
        id='yr-slider',
        min=2000,
        max=2020,
        step=1,
        marks=year_marks,
        tooltip={'always_visible': False, 'placement': 'bottom'}))),
],className='year-slider', style={"margin-left": "18rem", "margin-top": "4rem"})

chartLayout = html.Div([
    dbc.Row(
        # Region Map
        dbc.Col(dcc.Graph(id='chart-region', config={'displayModeBar': False},
                          style={'width': '150vh', 'height': '85vh', "padding-bottom": "2rem",}), xs={'size':12, 'offset':0}, 
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})
            ),
     html.Br(),
    dbc.Row(dbc.Col(dcc.Graph(id='chart-covid', config={'displayModeBar': False},
                              style={'width': '150vh', 'height': '85vh', "padding-bottom": "2rem",}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
     html.Br(),
    dbc.Row(dbc.Col(dcc.Graph(id='chart-vehicles', config={'displayModeBar': False},
                              style={'width': '150vh', 'height': '85vh', "padding-bottom": "2rem",}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
     html.Br(),
     html.Br(),
    dbc.Row(dbc.Col(dcc.Graph(id='chart-road', config={'displayModeBar': False},
                              style={'width': '150vh', 'height': '85vh', "padding-bottom": "2rem",}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
     html.Br(),
    dbc.Row(dbc.Col(dcc.Graph(id='chart-pie', config={'displayModeBar': False},
                              style={'width': '150vh', 'height': '85vh', "padding-bottom": "2rem",}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
     html.Br(),
     dbc.Row(dbc.Col(dcc.Graph(id='chart-top-roads', config={'displayModeBar': False},
                               style={'width': '150vh', 'height': '85vh', "padding-bottom": "2rem",}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
     html.Br(),
     html.Br(),
],className='chart-page', style={"margin-left": "19rem", "margin-top": "3.0rem"}) # html.Br(),


mapLayout = html.Div([
    dbc.Row(
        # Region Map
        dbc.Col(dcc.Graph(id='map-region', config={'displayModeBar': False},
                          style={'width': '160vh', 'height': '85vh'}), xs={'size':12, 'offset':0}, 
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})
            ),
    dbc.Row(dbc.Col(dcc.Graph(id='map-lad', config={'displayModeBar': False},
                              style={'width': '160vh', 'height': '85vh'}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
    dbc.Row(dbc.Col(dcc.Graph(id='map-region-lad', config={'displayModeBar': False},
                              style={'width': '160vh', 'height': '85vh'}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
    dbc.Row(dbc.Col(dcc.Graph(id='map-region-heatmap', config={'displayModeBar': False},
                              style={'width': '165vh', 'height': '85vh'}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
    dbc.Row(dbc.Col(dcc.Graph(id='map-lad-heatmap', config={'displayModeBar': False},
                              style={'width': '165vh', 'height': '85vh'}), xs={'size':12, 'offset':0},
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})),
],className='map-page', style={"margin-left": "14rem"})


homemapLayout = html.Div([
    dbc.Row(
        # Region Map
        dbc.Col(dcc.Graph(id='map-road', config={'displayModeBar': False},
                          style={'width': '160vh', 'height': '85vh'}), xs={'size':12, 'offset':0}, 
                    sm={'size':12, 'offset':0}, md={'size': 12, 'offset': 0},lg={'size': 6, 'offset': 0})
            ),
],className='map-page-road', style={"margin-left": "14rem", "margin-top": "0rem"})

##map layout
app.layout = html.Div([dcc.Location(id="url"), logo, content])

# geo map
@app.callback(
    Output('map-region', 'figure'),
    [Input('vehicle-dropdown', 'value'),Input('year-dropdown', 'value')])
def update_figure1(selected_vehicle, selected_year):
    filter_uk_geojson = df_uk_geojson_pq[(df_uk_geojson_pq["year"] == selected_year) & (df_uk_geojson_pq["vehicles"] == selected_vehicle)].copy()
    
    # map for uk 
    fig_map = go.Figure(go.Choroplethmapbox(geojson=uk_data, locations=filter_uk_geojson.id, featureidkey="properties.id", 
                            z=filter_uk_geojson.traffic_volume,
                            colorscale="YlOrRd",
                            colorbar=dict(thickness=30, ticklen=3, x=0.85,len=0.7, 
                                          title=dict(
                                              text="Volume of traffic",
                                              font={"color": "#ffffff", "family": "Cambria", "size":16},
                                              ),
                                          ticks="outside",
                                          tickfont={"family": "Cambria", "color": "#ffffff", "size":16}
                                          ),
                            # coloraxis='coloraxis',
                            text=filter_uk_geojson.region_name,
                            hovertemplate = 
                            '<br><b>Miles travelled</b>: %{z:.0f}<br>'+
                            '<b>Region</b>: %{text}<extra></extra>',
                            marker_opacity=0.95))
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_style='carto-darkmatter',
        mapbox_zoom=4.5, mapbox_center = {"lat": 54.55, "lon":-2.20},
        width=1260,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606')
    fig_map.update_traces(showscale=True)

    return fig_map
    
# geo road map
@app.callback(
    Output('map-road', 'figure'),
    [Input('road-dropdown', 'value')])
def update_figure2(selected_road):
    filter_uk_road = road_dict[selected_road]
    
    # map for uk 
    fig_map_rd = go.Figure(go.Scattermapbox(
        lat=filter_uk_road.latitude.values.tolist(),
        lon=filter_uk_road.longitude.values.tolist(),
        mode="markers+lines",
        line=dict(width=1, color='crimson'),
        marker=dict(
            size= (1.75 if selected_road == "All" else 2.5),
            color = 'gold',
            opacity = 0.8,
        ),
        text=filter_uk_road.road_number.values.tolist(),
        hovertemplate =
        '<b>Latitude</b>: %{lat:.2f}'+
        '<br><b>Longitude</b>: %{lon:.2f}<br>'+
        '<b>Road number</b>: %{text}<extra></extra>',
        opacity=0.4,
    )
    )

    fig_map_rd.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=go.layout.Mapbox(
            style= "carto-darkmatter",
            zoom=4.5, 
            center_lat = 54.5,
            center_lon = -2.24,
            accesstoken=mapbox_token,
        ),
        width=1260,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606'
    )

    return fig_map_rd
    
@app.callback(
    Output('map-lad', 'figure'),
    [Input('vehicle-dropdown', 'value'),Input('year-dropdown', 'value')])
def update_figure2(selected_vehicle, selected_year):
    filter_uk_lad = df_uk_lad_geojson_pq[(df_uk_lad_geojson_pq["year"] == selected_year) & (df_uk_lad_geojson_pq["vehicles"] == selected_vehicle)].copy()
    
    # map for uk 
    fig_map2 = go.Figure(go.Choroplethmapbox(geojson=lad_data, locations=filter_uk_lad.id, featureidkey="properties.id", 
                    z=filter_uk_lad.traffic_volume,
                    colorscale="YlOrRd",
                    colorbar=dict(thickness=30, ticklen=3, x=0.85,len=0.7,
                                  title=dict(
                                      text="Volume of traffic",
                                      font={"color": "#ffffff", "family": "Cambria", "size":16},
                                      ),
                                  ticks="outside",
                                  tickfont={"family": "Cambria", "color": "#ffffff", "size":16}
                                  ),
                    # coloraxis='coloraxis',
                    text=filter_uk_lad.LAD13NM,
                    hovertemplate = 
                    '<br><b>Miles travelled</b>: %{z:.0f}<br>'+
                    '<b>Local Authority</b>: %{text}<extra></extra>',
                    marker_opacity=0.9))
    fig_map2.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_style='carto-darkmatter',
        mapbox_zoom=4.5, mapbox_center = {"lat": 54.55, "lon":-2.20},
        width=1260,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606')
    fig_map2.update_traces(showscale=True)

    return fig_map2
    
@app.callback(
    Output('map-region-lad', 'figure'),
    [Input('vehicle-dropdown', 'value'),Input('year-dropdown', 'value'), Input('region-dropdown', 'value')])
def update_figure3(selected_vehicle, selected_year, selected_region):
    filter_uk_reglad = df_uk_lad_geojson_pq[(df_uk_lad_geojson_pq["year"] == selected_year) & (df_uk_lad_geojson_pq["vehicles"] == selected_vehicle) &
                                         (df_uk_lad_geojson_pq["region_name"] == selected_region)].copy()

    lad_lat_cen = df_uk_aadf_pq[df_uk_aadf_pq["region_name"] == selected_region]["latitude"].mean()
    lad_long_cen = df_uk_aadf_pq[df_uk_aadf_pq["region_name"] == selected_region]["longitude"].mean()
    # map for uk 
    fig_map3 = go.Figure(go.Choroplethmapbox(geojson=lad_data, locations=filter_uk_reglad.id, featureidkey="properties.id", 
                    z=filter_uk_reglad.traffic_volume,
                    colorscale="YlOrRd",
                    colorbar=dict(thickness=30, ticklen=3, x=0.85,len=0.7,
                                  title=dict(
                                      text="Volume of traffic",
                                      font={"color": "#ffffff", "family": "Cambria", "size":16},
                                      ),
                                  ticks="outside",
                                  tickfont={"family": "Cambria", "color": "#ffffff", "size":16}
                                  ),
                    # coloraxis='coloraxis',
                    text=filter_uk_reglad.LAD13NM,
                    hovertemplate = 
                    '<br><b>Miles travelled</b>: %{z:.0f}<br>'+
                    '<b>Local Authority</b>: %{text}<extra></extra>',
                    marker_opacity=0.9))
    fig_map3.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_style='carto-darkmatter',
        mapbox_zoom=9.3, mapbox_center = {"lat": lad_lat_cen, "lon":lad_long_cen},
        width=1260,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606')
    fig_map3.update_traces(showscale=True)

    return fig_map3
    
# geo region heatmap
@app.callback(
    Output('map-region-heatmap', 'figure'),
    [Input('vehicle-dropdown', 'value'),Input('year-dropdown', 'value')])
def update_figure4(selected_vehicle, selected_year):
    filter_uk_aadf = df_uk_aadf_pq[(df_uk_aadf_pq["year"] == selected_year) & (df_uk_aadf_pq["vehicles"] == selected_vehicle)].copy()
    
    # map for uk 
    fig_map4 = go.Figure(go.Densitymapbox(lat=filter_uk_aadf.latitude, lon=filter_uk_aadf.longitude, z=filter_uk_aadf.vehicles_aadf,
                                 radius=5, colorscale="Blackbody_r", 
                                 colorbar=dict(thickness=30, ticklen=3, x=0.85,len=0.7,
                                               title=dict(
                                                   text="Annual Average Daily Flow",
                                                   font={"color": "#ffffff", "family": "Cambria", "size":16},
                                                   ),
                                               ticks="outside",
                                               tickfont={"family": "Cambria", "color": "#ffffff", "size":16}
                                               ),
                                 text=filter_uk_aadf.region_name,
                                 hovertemplate = 
                                 '<br><b>Region</b>: %{text}<br>'+
                                 '<br><b>Annual Average Daily Flow</b>: %{z:.0f}<br><extra></extra>',
                                 opacity=0.9,
                                 showscale=True)
)
    fig_map4.add_trace(go.Scattermapbox(
                lat=df_road_geojson.latitude.values.tolist(),
                lon=df_road_geojson.longitude.values.tolist(),
                mode="lines",
                line=dict(width=0.75, color='darkcyan'),
                text=df_road_geojson.road_number.values.tolist(),
                hovertemplate =
                '<b>Latitude</b>: %{lat:.2f}'+
                '<br><b>Longitude</b>: %{lon:.2f}<br>'+
                '<b>Road number</b>: %{text}<extra></extra>',
                opacity=0.25,
            ))
    fig_map4.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_style='carto-darkmatter',
        mapbox_zoom=4.5, mapbox_center = {"lat": 54.55, "lon":-2.20},
        mapbox_accesstoken=mapbox_token,
        width=1261,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606')

    return fig_map4
    
@app.callback(
    Output('map-lad-heatmap', 'figure'),
    [Input('vehicle-dropdown', 'value'),Input('year-dropdown', 'value'), Input('region-dropdown', 'value')])
def update_figure5(selected_vehicle, selected_year, selected_region):
    filter_uk_reg_aadf = df_uk_aadf_pq[(df_uk_aadf_pq["year"] == selected_year) & (df_uk_aadf_pq["vehicles"] == selected_vehicle) &
                                         (df_uk_aadf_pq["region_name"] == selected_region)].copy()

    lad_lat_cen = df_uk_aadf_pq[df_uk_aadf_pq["region_name"] == selected_region]["latitude"].mean()
    lad_long_cen = df_uk_aadf_pq[df_uk_aadf_pq["region_name"] == selected_region]["longitude"].mean()
    # map for uk 
    fig_map5 = go.Figure(go.Densitymapbox(lat=filter_uk_reg_aadf.latitude, lon=filter_uk_reg_aadf.longitude, z=filter_uk_reg_aadf.vehicles_aadf,
                                 radius=25, colorscale="Blackbody_r", 
                                 colorbar=dict(thickness=30, ticklen=3, x=0.85,len=0.7,
                                               title=dict(
                                                   text="Annual Average Daily Flow",
                                                   font={"color": "#ffffff", "family": "Cambria", "size":16},
                                                   ),
                                               ticks="outside",
                                               tickfont={"family": "Cambria", "color": "#ffffff", "size":16}
                                               ),
                                 text=filter_uk_reg_aadf.region_name,
                                 hovertemplate = 
                                 '<br><b>Region</b>: %{text}<br>'+
                                 '<br><b>Annual Average Daily Flow</b>: %{z:.0f}<br><extra></extra>',
                                 opacity=0.9,
                                 showscale=True)
)
    fig_map5.add_trace(go.Scattermapbox(
                lat=df_road_geojson.latitude.values.tolist(),
                lon=df_road_geojson.longitude.values.tolist(),
                mode="lines",
                line=dict(width=0.75, color='darkcyan'),
                text=df_road_geojson.road_number.values.tolist(),
                hovertemplate =
                '<b>Latitude</b>: %{lat:.2f}'+
                '<br><b>Longitude</b>: %{lon:.2f}<br>'+
                '<b>Road number</b>: %{text}<extra></extra>',
                opacity=0.25,
            ))
    fig_map5.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_style='carto-darkmatter',
        mapbox_zoom=9.3, mapbox_center = {"lat": lad_lat_cen, "lon":lad_long_cen},
        mapbox_accesstoken=mapbox_token,
        width=1261,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606')

    return fig_map5

@app.callback(
    Output('chart-region', 'figure'),
    [Input('veh-dropdown', 'value'),Input('reg-dropdown', 'value'), Input('yr-slider', 'value')])
def update_chart1(selected_vehicle, selected_region, sel_year_range):

    filter_uk_df = uk_traffic_volume[(uk_traffic_volume["vehicles"] == selected_vehicle)].copy()
    if bool(selected_region):
      filter_uk_df = uk_traffic_volume[(uk_traffic_volume["vehicles"] == selected_vehicle) & (uk_traffic_volume["region_name"].isin(selected_region))].copy()
    #colors
    colors = ['lightslategray', 'crimson', 'darkcyan', 'darkgoldenrod', 'cornsilk', 'turquoise', 'limegreen', \
              'darkorchid', 'palevioletred', 'forestgreen', 'silver', 'lightsteelblue']

    filter_uk_df = filter_uk_df[(filter_uk_df.year >= 2000)&(filter_uk_df.year <= 2020)].copy()
    start,end = 2000,2020
    if bool(sel_year_range):
        # Filter the years of the data to be within range
        filter_uk_df = filter_uk_df[(filter_uk_df.year >= sel_year_range[0])&(filter_uk_df.year <= sel_year_range[1])].copy()
        start,end = sel_year_range[0],sel_year_range[1]
        diff = sel_year_range[1] - sel_year_range[0]
        colors = colors[:diff]

    # region_chart 
    fig_chart = px.line(filter_uk_df, x="year", y="traffic_volume", 
                      color="region_name", color_discrete_sequence = colors, template="plotly_dark",
                      markers=True)
    fig_chart.update_traces(textposition="bottom right")
    fig_chart.update_layout(
        title=f"<b> Volume of Traffic Trends for {selected_vehicle}, {start} - {end} <b>",
        xaxis_title="Years",
        yaxis_title="Volume of Traffic",
        legend_title="Regions",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="white"
            ),
        width=1150,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606'
    )
    return fig_chart
    
@app.callback(
    Output('chart-covid', 'figure'),
    [Input('veh-dropdown', 'value'), Input('yr-slider', 'value')])
def update_chart2(selected_vehicle, sel_year_range):

    filter_uk_df = vehicle_traffic_volume[vehicle_traffic_volume["vehicles"] == selected_vehicle].copy()
    if sel_year_range:
        # Filter the years of the data to be within range
        filter_uk_df = filter_uk_df[(filter_uk_df.year >= sel_year_range[0])&(filter_uk_df.year <= sel_year_range[1])].copy()
        diff = sel_year_range[1] - sel_year_range[0]
    else:
        # I created this becuase i kept getting NonType errors with all of my graph call backs
        filter_uk_df = filter_uk_df[(filter_uk_df.year >= 2000)&(filter_uk_df.year <= 2020)].copy()
        diff = 20

    #colors
    colors = ['lightslategray',] * (diff+1)
    colors[diff] = 'crimson'
    
    # region chart
    fig_chart1 = go.Figure()
    fig_chart1.add_trace(go.Bar(x=filter_uk_df["year"], y=filter_uk_df["traffic_volume"],
                         marker_color=colors))
    fig_chart1.update_layout(
        title_text='<b> Covid Impact on Road Traffic <b>',
        xaxis_title="Years",
        yaxis_title="Volume of Traffic",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="white"
            ),
        template="plotly_dark",
        width=1150,height=620,
        paper_bgcolor='#060606',
        plot_bgcolor='#060606'
      )
    
    return fig_chart1
    
@app.callback(
    Output('chart-vehicles', 'figure'),
    [Input('year-diff-dropdown', 'value')])
def update_chart3(selected_yr_diff):

    yr_split = selected_yr_diff.split("-")
    traffic_yr1 = vehicle_traffic_volume[vehicle_traffic_volume["year"] == int(yr_split[0])].reset_index(drop=True).copy()
    traffic_yr2 = vehicle_traffic_volume[vehicle_traffic_volume["year"] == int(yr_split[1])].reset_index(drop=True).copy()

    traffic_yr2["volume_diff"] = (traffic_yr2["traffic_volume"] - traffic_yr1["traffic_volume"]) \
    / (traffic_yr2["traffic_volume"] + traffic_yr1["traffic_volume"])
    traffic_yr2["volume_diff"] *= 100

    #colors
    diff_color = ["steelblue" if val > 0 else "crimson" for val in traffic_yr2["volume_diff"]]
    
    # region chart
    fig_chart2 = go.Figure()
    fig_chart2.add_trace(go.Bar(x=traffic_yr2["vehicles"], y=traffic_yr2["volume_diff"],
                                marker_color= diff_color))
    fig_chart2.update_layout(
    title_text=f'<b> Change in miles travelled by vehicle type in UK, {yr_split[0]}-{yr_split[1]} <b>',
    xaxis_title="",
    yaxis_title="Percent Change %",
    font=dict(
        family="Courier New, monospace",
        size=16,
        color="white"
        ),
    width=1150, height=700, 
    template="plotly_dark",
    paper_bgcolor='#060606',
    plot_bgcolor='#060606'
    )
    
    return fig_chart2
    
@app.callback(
    Output('chart-road', 'figure'),
    [Input('year-diff-dropdown', 'value')])
def update_chart4(selected_yr_diff):

    yr_split = selected_yr_diff.split("-")
    traffic_yr1 = rd_category_agg[rd_category_agg["year"] == int(yr_split[0])].reset_index(drop=True).copy()
    traffic_yr2 = rd_category_agg[rd_category_agg["year"] == int(yr_split[1])].reset_index(drop=True).copy()

    traffic_yr2["volume_diff"] = (traffic_yr2["traffic_volume"] - traffic_yr1["traffic_volume"]) \
    / (traffic_yr2["traffic_volume"] + traffic_yr1["traffic_volume"])
    traffic_yr2["volume_diff"] *= 100

    #colors
    diff_color = ["steelblue" if val > 0 else "crimson" for val in traffic_yr2["volume_diff"]]
    
    # region chart
    fig_chart3 = go.Figure()
    fig_chart3.add_trace(go.Bar(x=traffic_yr2["road_category"], y=traffic_yr2["volume_diff"],
                                marker_color= diff_color))
    fig_chart3.update_layout(
    title_text=f'<b>Percent change in miles travelled across Road Category in UK, {yr_split[0]}-{yr_split[1]} <b>',
    xaxis_title="",
    yaxis_title="Percent Change %",
    font=dict(
        family="Courier New, monospace",
        size=16,
        color="white"
        ),
    width=1150, height=650,
    template="plotly_dark",
    paper_bgcolor='#060606',
    plot_bgcolor='#060606'
    )
    
    return fig_chart3
    
@app.callback(
    Output('chart-pie', 'figure'),
    [Input('veh-dropdown', 'value'), Input('yr-dropdown', 'value')])
def update_chart5(selected_veh, selected_year):

    filtered_df = veh_rd_traffic_volume[(veh_rd_traffic_volume["vehicles"] == selected_veh) & (veh_rd_traffic_volume["year"] == selected_year)].copy()

    miles_text = f"{(round(filtered_df.traffic_volume.sum())//1000000000)} Billion Miles" if (round(filtered_df.traffic_volume.sum())//1000000000) \
    else f"{(round(filtered_df.traffic_volume.sum())//1000000)} Million miles"
    pie_color = ['lightslategray', 'cornsilk', 'turquoise', 'crimson']
    
    # region chart
    fig_chart4 = go.Figure()
    fig_chart4.add_trace(go.Pie(labels=filtered_df["road_category"], 
                                values=filtered_df["traffic_volume"], 
                                marker_colors=pie_color,
                                name="Miles Driven"))
    
    # Use `hole` to create a donut-like pie chart
    fig_chart4.update_traces(hole=.55, hoverinfo="label+percent+name")
    fig_chart4.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text=miles_text, x=0.50, y=0.58, font_size=20, showarrow=False),
                     dict(text=f'Covered in {selected_year}', x=0.50, y=0.53, font_size=20, showarrow=False),
                     dict(text=f'by {selected_veh}', x=0.50, y=0.48, font_size=18, showarrow=False)],
                     width=1150, height=650)
    fig_chart4.update_layout(
        title_text=f'<b> Volume of Traffic across major road categories,{selected_year} <b>',
        font=dict(
            family="Courier New, monospace",
            size=16,
            color="white"
            ),
        template="plotly_dark",
        paper_bgcolor='#060606',
        plot_bgcolor='#060606'
        )
    
    return fig_chart4
    
@app.callback(
    Output('chart-top-roads', 'figure'),
    [Input('veh-dropdown', 'value'), Input('yr-dropdown', 'value')])
def update_chart6(selected_veh, selected_year):

    filtered_df = rd_type_traffic_volume[(rd_type_traffic_volume["vehicles"] == selected_veh) & (rd_type_traffic_volume["year"] == selected_year)].copy()
    filtered_df.sort_values(by=['traffic_volume'], ascending=False, inplace=True)

    # region chart
    fig_chart5 = px.bar(filtered_df, x= "traffic_volume", y= "road_name", color='road_name', orientation = 'h', 
                        pattern_shape="road_name", pattern_shape_sequence=[".", "x", "+",".", '/', '\\', 'x', '-', '|', "+","."],
                        labels={'year':'<b> Years <b>'}, template="plotly_dark",
                        color_discrete_sequence = px.colors.sequential.YlOrRd_r)
    
    fig_chart5.update_layout(
        title_text=f'<b> Volume of Traffic across Major Roads, {selected_year} ({selected_veh}) <b>',
        xaxis_title="Volume of Traffic",
        yaxis_title="Major Roads",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="white"
            ),
        width=1150, height=700,
        showlegend=False,
        template="plotly_dark",
        paper_bgcolor='#060606',
        plot_bgcolor='#060606'
    )

    return fig_chart5
    
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == '/':
        return sidebar_2, html.Div([
                         dcc.Markdown('''

            ### Traffic Analytics United Kingdom
            This dashboard is a portfolio project built by [Adeniyi Adeboye](https://github.com/AdeboyeML?tab=repositories) using Plotly's Dash,
            It focuses on giving detailed insights into the evolution of road traffic trends across the United Kingdom between 2000 - 2020.
        ''')],className='home'),homemapLayout
    elif pathname == '/maps':
        return sidebar, mapLayout
    elif pathname == '/charts':
        return sidebar_1,yearSlider,chartLayout
    else:
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)