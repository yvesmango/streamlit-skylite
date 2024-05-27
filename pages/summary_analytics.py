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


# Access the DataFrame from session state
if 'df' in st.session_state:
    df = st.session_state.df
    if isinstance(df, pd.DataFrame):
        # Ensure the necessary columns are present
        required_columns = ['coordinates_origin', 'coordinates_destination', 'municipality_origin', 'municipality_destination', 'iso_region_origin', 'iso_region_destination', 'flightDuration']
        if all(column in df.columns for column in required_columns):
            # Do something with df
            st.write(df.head())
            
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
if 'df' in st.session_state:
    df = st.session_state.df
    region_pairs = df.groupby(['origin', 'destination']).size().reset_index(name='count').sort_values(by='count', ascending=False).head(10).reset_index(drop=True)
    st.write("### Top 10 Flight Origin/Destination Pairs")
    st.table(region_pairs)
else:
    st.write("No data available in session state.")



# flight duration histogram
if 'df' in st.session_state:
    fig = px.histogram(df, x="flight_minutes", nbins=30, title='Histogram: Flight Duration (minutes)')
    st.plotly_chart(fig, theme="streamlit")    



# Top flown airlines
if 'df' in st.session_state:

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












