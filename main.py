from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

gdf = gpd.read_file("/Users/harsnyi/Documents/NYC-Crash-Analysis/nyc.geojson")
df = pd.read_csv("/Users/harsnyi/Documents/NYC-Crash-Analysis/data/NYC_crashes_weather_combined.csv")
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
    opacity=0.5,
)

latitudes = df_sampled['LATITUDE']
longitudes = df_sampled['LONGITUDE']

borough_colors = {
    'MANHATTAN': '#058ED9',
    'BROOKLYN': '#17C3B2',
    'QUEENS': '#BF3100',
    'BRONX': '#EC9F05',
    'STATEN ISLAND': '#912F56'
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
    ),
    paper_bgcolor='#BEBBBB',
    plot_bgcolor='#E8E8E8'
)

unique_years = sorted(df['YEAR'].dropna().unique())
years_int = [int(year) for year in unique_years]

app.layout = html.Div(
    children=[
        html.H1("NYC Crash Analysis", style={
            "marginBottom": "20px",
            "width": "100%",
            "text-align": "center",
            "font-size": "40px"}),

        html.Div(
            children=[
                html.H3("Filter by Year and Month", style={"marginTop": "40px"}),

                html.Div(
                    children=[
                        html.Div(
                            children=[
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
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "marginRight": "20px",
                                "flex": "1",
                            }
                        ),

                        html.Div(
                            children=[
                                html.Img(
                                    src="/assets/car-crash.svg",
                                    style={
                                        "width": "300px",
                                        "height": "auto",
                                    }
                                ),
                            ],
                            style={
                                "flex": "0",
                            }
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "alignItems": "center",
                        "justifyContent": "flex-start",
                        "padding": "0 0",
                    }
                ),

                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id='new-hour-histogram',
                                    style={"flex": "1", "marginRight": "10px", "height": "400px"},
                                ),
                                dcc.Graph(
                                    id='borough-pie-chart',
                                    style={"flex": "1", "marginLeft": "10px", "height": "400px"},
                                ),
                                dcc.Graph(
                                    id='vehicle-type-distribution',
                                    style={"flex": "1", "marginRight": "10px", "height": "400px"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "row",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "width": "100%",
                                "padding": "10px 0",
                                "border-radius": "5px"
                            }
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            id='borough-bar-chart',
                                            style={"flex": "1", "marginRight": "10px", "height": "400px"},
                                        ),
                                        dcc.Graph(
                                            id='crash-precipitation-line-chart',
                                            style={"flex": "1", "marginLeft": "10px", "height": "400px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "row",
                                        "justifyContent": "space-between",
                                        "alignItems": "center",
                                        "width": "100%",
                                        "padding": "10px 0",
                                        "border-radius": "5px"
                                    }
                                ),
                            ]
                        )
                    ]
                )
            ],
            style={
                "backgroundColor": "#f0f0f0",
                "padding": "20px",
                "borderRadius": "10px",
                "marginBottom": "20px"
            }
        ),
        
        dcc.Slider(
            2013,
            2023,
            step=None,
            marks={year: f"{year}" for year in years_int},
            tooltip={"always_visible": True},
            id="my-slider"
        ),

        dcc.Graph(id='map-graph', figure=fig_map, style={"width": "80%", "height": "600px"}),
        
    ],
    style={
        "padding": "20px",
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

    latitudes = df_sampled['LATITUDE']
    longitudes = df_sampled['LONGITUDE']
    colors = df_sampled['BOROUGH'].map(borough_colors)

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


@callback(
    [
        Output('new-hour-histogram', 'figure'),
        Output('borough-pie-chart', 'figure')
    ],
    [
        Input('new-year-toggle', 'value'),
        Input('new-month-toggle', 'value')
    ]
)
def update_hour_histogram(selected_years, selected_months):
    filtered_df = df[(df['YEAR'].isin(selected_years)) & (df['MONTH'].isin(selected_months))]

    new_histogram = go.Figure()
    if not filtered_df.empty:
        new_histogram.add_trace(go.Histogram(
            x=filtered_df['HOUR'],
            nbinsx=24,
            marker=dict(color='#F5BB00', opacity=0.8),
            name='Incidents by Hour'
        ))

        new_histogram.update_layout(
            title="Histogram of Incidents by Hour",
            xaxis_title="Hour",
            yaxis_title="Frequency",
            bargap=0.2,
            paper_bgcolor='#BEBBBB',
            plot_bgcolor='#E8E8E8',
            xaxis=dict(showgrid=True, gridcolor='gray'),
            yaxis=dict(showgrid=True, gridcolor='gray'),
        )
    else:
        new_histogram.update_layout(
            title=f"No Data Available for Years {selected_years} and Months {selected_months}",
            xaxis_title="Hour",
            yaxis_title="Frequency",
            plot_bgcolor='#E8E8E8',
            xaxis=dict(showgrid=True, gridcolor='gray'),
            yaxis=dict(showgrid=True, gridcolor='gray'),
        )

    pie_chart = go.Figure()
    if not filtered_df.empty:
        borough_counts = filtered_df['BOROUGH'].value_counts()
        pie_chart.add_trace(go.Pie(
            labels=borough_counts.index,
            values=borough_counts.values,
            hole=0.3,
            marker=dict(
                colors=[borough_colors.get(borough, 'gray') for borough in borough_counts.index]
            )
        ))

        pie_chart.update_layout(
            title="Incident Distribution by Borough",
            paper_bgcolor='#BEBBBB'
        )
    else:
        pie_chart.update_layout(
            title="No Data Available for Borough Distribution",
            paper_bgcolor='#BEBBBB'
        )

    return [new_histogram, pie_chart]

@callback(
    Output('vehicle-type-distribution', 'figure'),
    [Input('new-year-toggle', 'value'),
    Input('new-month-toggle', 'value')]
)
def update_vehicle_type_distribution(selected_years, selected_months):
    filtered_df = df[(df['YEAR'].isin(selected_years)) & (df['MONTH'].isin(selected_months))]

    vehicle_columns = ['VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3', 
                        'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5']

    filtered_df['vehicle_type_count'] = filtered_df[vehicle_columns].notna().sum(axis=1)

    vehicle_count_distribution = filtered_df['vehicle_type_count'].value_counts().reset_index()
    vehicle_count_distribution.columns = ['Vehicle Type Count', 'Frequency']
    vehicle_count_distribution = vehicle_count_distribution[vehicle_count_distribution["Vehicle Type Count"] > 0]

    fig = px.bar(vehicle_count_distribution, 
                y='Vehicle Type Count', 
                x='Frequency', 
                labels={'Vehicle Type Count': 'Number of Vehicles Involved', 'Frequency': 'Number of Crashes'},
                title="Count of Vehicles Involved in Crashes", 
                orientation='h')

    fig.update_layout(
        paper_bgcolor='#BEBBBB',
        plot_bgcolor='#E8E8E8',
        xaxis=dict(showgrid=True, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridcolor='gray')
    )

    return fig


@callback(
    Output('borough-bar-chart', 'figure'),
    [Input('new-year-toggle', 'value'), Input('new-month-toggle', 'value')]
)
def update_borough_bar_chart(selected_years, selected_months):
    filtered_df = df[(df['YEAR'].isin(selected_years)) & (df['MONTH'].isin(selected_months))]
    
    borough_data = filtered_df.groupby('BOROUGH').agg(
        Injured=('NUMBER OF PERSONS INJURED', 'sum'),
        Killed=('NUMBER OF PERSONS KILLED', 'sum')
    ).reset_index()

    bar_chart = go.Figure()

    bar_chart.add_trace(go.Bar(
        x=borough_data['BOROUGH'],
        y=borough_data['Injured'],
        name='Number Injured',
        marker=dict(color='#97C4B1')
    ))

    bar_chart.add_trace(go.Bar(
        x=borough_data['BOROUGH'],
        y=borough_data['Killed'],
        name='Number Killed',
        marker=dict(color='#D76A03')
    ))

    bar_chart.update_layout(
        barmode='group',
        title="Injuries and Fatalities by Borough",
        xaxis_title="Borough",
        yaxis_title="Count",
        paper_bgcolor='#BEBBBB',
        plot_bgcolor='#E8E8E8',
        xaxis=dict(showgrid=True, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridcolor='gray'),
        legend=dict(title="Metrics")
    )

    return bar_chart

@callback(
    Output('crash-precipitation-line-chart', 'figure'),
    [Input('new-year-toggle', 'value'),
     Input('new-month-toggle', 'value')]
)
def update_crash_precipitation_line_chart(selected_years, selected_months):
    filtered_df = df[(df['YEAR'].isin(selected_years)) & (df['MONTH'].isin(selected_months))]

    monthly_data = filtered_df.groupby(['YEAR', 'MONTH']).agg(
        crash_count=('crash_time', 'size'),
        sum_precipitation=('precipitation (mm)', 'sum')
    ).reset_index()

    # Create the scatter plot
    scatter_plot = go.Figure()

    scatter_plot.add_trace(go.Scatter(
        x=monthly_data['sum_precipitation'],
        y=monthly_data['crash_count'],
        mode='markers',
        marker=dict(color='#F5BB00', opacity=0.8),
        text=monthly_data['YEAR'].astype(str) + '-' + monthly_data['MONTH'].astype(str),
        hoverinfo='text',
    ))

    # Update layout
    scatter_plot.update_layout(
        title="Crash Count vs Precipitation",
        xaxis_title="Total Precipitation (mm)",
        yaxis_title="Crash Count",
        paper_bgcolor='#BEBBBB',
        plot_bgcolor='#E8E8E8',
        xaxis=dict(showgrid=True, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridcolor='gray'),
    )

    return scatter_plot

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
