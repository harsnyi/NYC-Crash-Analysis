from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

# Load GeoDataFrame and CSV file
gdf = gpd.read_file("/Users/harsnyi/Documents/NYC-Crash-Analysis/nyc.geojson")
df = pd.read_csv("/Users/harsnyi/Documents/NYC-Crash-Analysis/data/records.csv")
df = df[df["BOROUGH"].notnull()]
df_sampled = df.sample(n=1000)

# Ensure the CRS is compatible with Mapbox (EPSG:4326)
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")


# Create a Dash app
# Create a Dash app with suppress_callback_exceptions enabled
app = Dash(__name__, suppress_callback_exceptions=True)


# Create a choropleth map
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

# Extract latitude and longitude from df
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


# Clustered markers
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
    name='Crash Incidents',  # Trace name
    text=df_sampled['HOUR'],  # Display crash location on hover
    hoverinfo='text'  # Show location text
))

# Update map layout to ensure proper display
fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox=dict(
        accesstoken="your_mapbox_access_token"  # Make sure to replace with your Mapbox token if needed
    )
)

# Create a histogram using Plotly for HOUR column
hist_fig = go.Figure()

hist_fig.add_trace(go.Histogram(
    x=df['HOUR'],
    nbinsx=len(df['HOUR'].unique()),  # Set number of bins to the number of unique hours
    marker=dict(color='blue', opacity=0.7),
    name='Incidents by Hour'
))

# Update histogram layout
hist_fig.update_layout(
    title="Histogram of Incidents by Hour",
    xaxis_title="Hour",
    yaxis_title="Frequency",
    bargap=0.2
)

unique_years = sorted(df['YEAR'].dropna().unique())
years_int = [int(year) for year in unique_years]

# Dash app layout with the map and the histogram
app.layout = html.Div(
    children=[
        html.H1("NYC Crash Analysis Map", style={"marginBottom": "20px"}),
        
        
        dcc.Slider(
            2012,
            2024,
            step=None,
            marks={year: f"{year}" for year in years_int},
            tooltip={"always_visible": True},
            id="my-slider",
        ),
        html.Div(id='slider-output-container'),

        
        dcc.Graph(id='map-graph', figure=fig_map, style={"width": "80%", "height": "600px"}),

        # Add the histogram below the map
        html.H3("Histogram of Incidents by Hour", style={"marginTop": "40px"}),
        dcc.Graph(id='hist-graph', figure=hist_fig, style={"width": "80%", "height": "400px"})
    ]
)

@callback(
    [Output('slider-output-container', 'children'),
     Output('map-graph', 'figure'),
     Output('hist-graph', 'figure')],  # Add Output for histogram
    [Input('my-slider', 'value')]
)
def update_map_and_histogram(value):
    
    # Filter the data based on the selected year
    filtered_df = df[df['YEAR'] == value]
    
    # Check if the filtered DataFrame has fewer than 1000 rows
    sample_size = min(len(filtered_df), 1000)  # Sample up to 1000 rows, but no more
    
    # Sample the data
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
        name='Crash Incidents',  # Trace name
        text=df_sampled['LOCATION'],  # Display crash location on hover
        hoverinfo='text'  # Show location text
    ))

    # Update the histogram with the filtered data
    hist_fig = go.Figure()

    hist_fig.add_trace(go.Histogram(
        x=df_sampled['HOUR'],
        nbinsx=len(df_sampled['HOUR'].unique()),  # Set number of bins to the number of unique hours
        marker=dict(color='blue', opacity=0.7),
        name='Incidents by Hour'
    ))

    # Update histogram layout
    hist_fig.update_layout(
        title=f"Histogram of Incidents by Hour for {value}",
        xaxis_title="Hour",
        yaxis_title="Frequency",
        bargap=0.2
    )

    return f"Selected Year: {value}", fig_map, hist_fig  # Return both map and histogram


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
