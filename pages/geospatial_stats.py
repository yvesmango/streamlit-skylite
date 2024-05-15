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
import geopandas as gpd
import pydeck as pdk

st.write("### <under constructioning>")

# Access the DataFrame from session state
if 'df' in st.session_state:
    df = st.session_state.df
    if isinstance(df, pd.DataFrame):
        # Ensure the necessary columns are present
        required_columns = ['coordinates_origin', 'coordinates_destination', 'municipality_origin', 'municipality_destination']
        if all(column in df.columns for column in required_columns):
            # Do something with df
            st.write(df.head())
            
            # Create a new DataFrame with only the required columns
            df_subset = df[required_columns]
            
            # Define a layer to display on a map
            layer = pdk.Layer(
                "GreatCircleLayer",
                df_subset,
                pickable=True,
                get_stroke_width=7,
                get_source_position="coordinates_origin",
                get_target_position="coordinates_destination",
                get_source_color=[64, 255, 0],
                get_target_color=[0, 128, 200],
                auto_highlight=True,
            )

            # Define tooltip dictionary
            tooltip = {
                "html": "<b>Origin:</b> {municipality_origin}<br/><b>Destination:</b> {municipality_destination}",
                "style": {"backgroundColor": "white", "color": "black"}
            }

            # Render the arc map
            st.pydeck_chart(pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                    latitude=37.76,
                    longitude=-122.4,
                    zoom=4,
                    pitch=50,
                ),
                layers=[layer],
                tooltip=tooltip  # Added tooltip to Deck configuration
            ))
        else:
            st.write("Warning: DataFrame is missing required columns.")
    else:
        st.write("Warning: Data found in session state is not a DataFrame.")
else:
    st.write("Warning: Data not found in session state, please visit About Me page to reload data properly.")
