from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

gdf = gpd.read_file("/Users/harsnyi/Documents/NYC-Crash-Analysis/nyc.geojson")
df = pd.read_csv("/Users/harsnyi/Documents/NYC-Crash-Analysis/data/NYC_crashes.csv")
df = df[df["BOROUGH"].notnull()]
df_sampled = df.sample(n=1000)
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")


app = Dash(__name__, suppress_callback_exceptions=True)

fig_map = px.choropleth_mapbox(
    gdf,
    geojson=gdf.__geo_interface__,
    locations=gdf.index,
    color="BoroName",
    hover_name="BoroName",
    mapbox_style="carto-positron",
    center={"lat": 40.7128, "lon": -74.0060},
    zoom=10,
    opacity=0.5
)

latitudes = df_sampled['LATITUDE']
longitudes = df_sampled['LONGITUDE']

borough_colors = {
    'MANHATTAN': 'blue',
    'BROOKLYN': 'green',
    'QUEENS': 'red',
    'BRONX': 'yellow',
    'STATEN ISLAND': 'purple'
}
colors = df_sampled['BOROUGH'].map(borough_colors)

fig_map.add_trace(go.Scattermapbox(
    lat=latitudes,
    lon=longitudes,
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=8,
        color=colors,
        opacity=0.7,
        cauto=True
    ),
    name='Crash Incidents',
    text=df_sampled['HOUR'],
    hoverinfo='text'
))

fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox=dict(
        accesstoken="your_mapbox_access_token"
    )
)

hist_fig = go.Figure()

hist_fig.add_trace(go.Histogram(
    x=df['HOUR'],
    nbinsx=len(df['HOUR'].unique()),
    marker=dict(color='blue', opacity=0.7),
    name='Incidents by Hour'
))

hist_fig.update_layout(
    title="Histogram of Incidents by Hour",
    xaxis_title="Hour",
    yaxis_title="Frequency",
    bargap=0.2
)

unique_years = sorted(df['YEAR'].dropna().unique())
years_int = [int(year) for year in unique_years]

app.layout = html.Div(
    children=[
        html.H1("NYC Crash Analysis Map", style={"marginBottom": "20px"}),
        
        dcc.Slider(
            2013,
            2023,
            step=None,
            marks={year: f"{year}" for year in years_int},
            tooltip={"always_visible": True},
            id="my-slider",
        ),
        dcc.Graph(id='map-graph', figure=fig_map, style={"width": "80%", "height": "600px"}),
        html.H3("Filter by Year and Month", style={"marginTop": "40px"}),
        dcc.Checklist(
            options=[{"label": str(year), "value": year} for year in range(2013, 2024)],
            value=[2023],
            id="new-year-toggle",
            inline=True,
            className="toggle-buttons",
        ),

        dcc.Checklist(
            options=[{"label": str(month), "value": month} for month in range(1, 13)],
            value=[1],
            id="new-month-toggle",
            inline=True,
            className="toggle-buttons",
        ),

        # New Histogram for crashes by hour
        dcc.Graph(
            id='new-hour-histogram', style={"width": "80%", "height": "600px"}),
    ],
    style={
        "padding": "20px",
        "background-color": "#BEBBBB",
    }
)

@callback(
    [Output('map-graph', 'figure')],
    [Input('my-slider', 'value')]
)
def update_map_and_histogram(value):
    filtered_df = df[df['YEAR'] == value]
    sample_size = min(len(filtered_df), 1000)
    df_sampled = filtered_df.sample(n=sample_size)

    # Update the map with filtered data
    latitudes = df_sampled['LATITUDE']
    longitudes = df_sampled['LONGITUDE']
    colors = df_sampled['BOROUGH'].map(borough_colors)

    # Create the new map
    fig_map = px.choropleth_mapbox(
        gdf,
        geojson=gdf.__geo_interface__,
        locations=gdf.index,
        color="BoroName",
        hover_name="BoroName",
        mapbox_style="carto-positron",
        center={"lat": 40.7128, "lon": -74.0060},
        zoom=10,
        opacity=0.5
    )
    
    # Add scatter mapbox for crash incidents
    fig_map.add_trace(go.Scattermapbox(
        lat=latitudes,
        lon=longitudes,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=8,
            color=colors,
            opacity=0.7,
            cauto=True
        ),
        name='Crash Incidents',
        text=df_sampled['LOCATION'],
        hoverinfo='text'
    ))

    return [fig_map]


# Callback to update the new histogram
@callback(
    [
        Output('new-hour-histogram', 'figure')
    ],
    [
        Input('new-year-toggle', 'value'),
        Input('new-month-toggle', 'value')
    ]
)
def update_hour_histogram(selected_years, selected_months):
    # Filter data based on the selected years and months
    filtered_df = df[(df['YEAR'].isin(selected_years)) & (df['MONTH'].isin(selected_months))]

    # Create a new histogram for the filtered data
    new_histogram = go.Figure()

    if not filtered_df.empty:
        new_histogram.add_trace(go.Histogram(
            x=filtered_df['HOUR'],
            nbinsx=24,  # 24 bins for 24 hours
            marker=dict(color='orange', opacity=0.7),
            name='Incidents by Hour'
        ))

        new_histogram.update_layout(
            title="Histogram of Incidents by Hour",
            xaxis_title="Hour",
            yaxis_title="Frequency",
            bargap=0.2,
            paper_bgcolor='#BEBBBB'
        )
    else:
        new_histogram.update_layout(
            title=f"No Data Available for Years {selected_years} and Months {selected_months}",
            xaxis_title="Hour",
            yaxis_title="Frequency",
        )

    # Display the selected years and months
    year_output = f"Selected Years: {', '.join(map(str, selected_years))}"
    month_output = f"Selected Months: {', '.join(map(str, selected_months))}"

    return [new_histogram]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
