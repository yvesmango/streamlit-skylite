import json
from datetime import datetime
import streamlit as st
from streamlit_lottie import st_lottie
import google.auth
from google.oauth2 import service_account
from google.cloud import bigquery
import numpy as np
import pandas_gbq
import pandas as pd 
import plotly.express as px
import geopandas as gpd
import pydeck as pdk

st.write("## Summary Analytics")

# Function to convert string coordinates to lists
def convert_coordinates(coord_str):
    try:
        # Split the string and convert to floats
        lon, lat = map(float, coord_str.split(','))
        return [lon, lat]
    except Exception as e:
        st.write(f"Error converting coordinates: {coord_str} -> {e}")
        return None


# Ensure 'geo' is loaded in session state
if 'geo' in st.session_state:
    geo_data = st.session_state.geo
    
    # Calculate metrics
    total_distance_km = geo_data['distance_km'].sum()
    # Find minimum distance that is not zero
    min_distance_km = geo_data.loc[geo_data['distance_km'] > 0, 'distance_km'].min()
    max_distance_km = geo_data['distance_km'].max()
    

    # Round the values to 3 decimal places
    total_distance_rounded = round(total_distance_km, 3)
    min_distance_rounded = round(min_distance_km, 3)
    max_distance_rounded = round(max_distance_km, 3)
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Distance Traveled (km)", total_distance_rounded)
    col2.metric("Minimum Distance Traveled (km)", min_distance_rounded)
    col3.metric("Maximum Distance Traveled (km)", max_distance_rounded)
else:
    st.write("Geo Data (geo) not found in session state.")




# Access the DataFrame from session state
if 'df' in st.session_state:
    df = st.session_state.df
    if isinstance(df, pd.DataFrame):
        # Ensure the necessary columns are present
        required_columns = ['coordinates_origin', 'coordinates_destination', 'municipality_origin', 'municipality_destination', 'iso_region_origin', 'iso_region_destination', 'flightDuration']
        if all(column in df.columns for column in required_columns):
            # Do something with df
            
            st.write("### Flight history, visualized")
            
            # Create a new DataFrame with only the required columns
            df_subset = df[required_columns].copy()

            # Convert coordinate columns to lists of floats
            df_subset['coordinates_origin'] = df_subset['coordinates_origin'].apply(convert_coordinates)
            df_subset['coordinates_destination'] = df_subset['coordinates_destination'].apply(convert_coordinates)


            
            # Define a layer to display on a map
            layer = pdk.Layer(
                "GreatCircleLayer",
                df_subset,
                pickable=True,
                get_stroke_width=12,
                get_source_position="coordinates_origin",
                get_target_position="coordinates_destination",
                get_source_color=[64, 255, 0],
                get_target_color=[0, 128, 200],
                auto_highlight=True,
                
            )
            
            # Define a layer to display on a map
            scatterplot = pdk.Layer(
                "ScatterplotLayer",
                df_subset,
                pickable=True,
                opacity=0.7,
                filled=True,
                radius_scale=1,
                radius_min_pixels=2.5,
                radius_max_pixels=100,
                line_width_min_pixels=1,
                get_position="coordinates_origin",
                get_fill_color=[255, 140, 0]
            )         

            # Define tooltip dictionary
            tooltip = {
                "html": "<b>Origin:</b> {municipality_origin}, {iso_region_origin}<br/><b>Destination:</b> {municipality_destination}, {iso_region_destination}<br/><b>Flight Duration:</b> {flightDuration}",
                "style": {"backgroundColor": "white", "color": "black"}
            }

            # Render the arc map
            st.pydeck_chart(pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                    latitude=39.76,
                    longitude=-100.4,
                    zoom=3,
                    pitch=0,
                ),
                layers=[layer, scatterplot],
                tooltip=tooltip  # Added tooltip to Deck configuration
            ))
        else:
            st.write("Warning: DataFrame is missing required columns.")
    else:
        st.write("Warning: Data found in session state is not a DataFrame.")
else:
    st.write("Warning: Data not found in session state, please visit About Me page to reload data properly.")




# Count of Flights by Region Pair
if 'geo' in st.session_state:
    df = st.session_state.geo
    region_pairs = df.groupby(['origin', 'destination']).size().reset_index(name='count').sort_values(by='count', ascending=False).head(10).reset_index(drop=True)
    st.write("### Top 10 Flight Origin/Destination Pairs")
    st.table(region_pairs)
else:
    st.write("No data available in session state.")



# Top flown airlines
if 'geo' in st.session_state:

    # Calculate the top 10 airlines
    top_airlines = df['airline'].value_counts().nlargest(10)

    # Create a DataFrame from the top airlines data
    top_airlines_df = top_airlines.reset_index()
    top_airlines_df.columns = ['Airline', 'Count']

    # Create the horizontal bar plot using Plotly Express
    fig = px.bar(top_airlines_df, x='Count', y='Airline', orientation='h', 
                 title='Top 10 Airlines Flown', labels={'Count': 'Count', 'Airline': 'Airline'},
                 color='Airline')

    # Update layout for better appearance
    fig.update_layout(xaxis_title='Count', yaxis_title='Airline', showlegend=False)

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)


# flight duration histogram
if 'geo' in st.session_state:
    fig = px.histogram(df, x="flight_minutes", nbins=30, title='Histogram: Flight Duration (minutes)', color_discrete_sequence=['royalblue'])
    st.plotly_chart(fig, theme="streamlit")    



if 'geo' in st.session_state:
    geo_data = st.session_state.geo
    
    # Group by 'airline' and calculate average distance traveled
    grouped_distance = geo_data.groupby('airline')['distance_km'].sum().reset_index()
    
    # Round the average distances to 3 decimal places
    grouped_distance['distance_km'] = grouped_distance['distance_km']
    
    # Sort by average distance (optional)
    grouped_distance = grouped_distance.sort_values(by='distance_km', ascending=False)
    
    # Select top 10 airlines by average distance
    top_10_distance = grouped_distance.head(10)

    custom_palette = px.colors.qualitative.Set2
    
    # Create the horizontal bar plot using Plotly Express
    fig = px.bar(top_10_distance, x='distance_km', y='airline', orientation='h', 
                 title='Top 10 Airlines by Total Distance Traveled',
                 labels={'distance_km': 'Total Distance (km)', 'airline': 'Airline'},
                 color='airline', color_discrete_sequence=custom_palette)
    
    fig.update_traces(hovertemplate='Airline: %{y}<br>Total Distance (km): %{x:.3f}')

    # Update layout for better appearance
    fig.update_layout(xaxis_title='Total Distance (km)', yaxis_title='Airline', showlegend=False)
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Geo Data (geo) not found in session state.")



# Top flown equipment

