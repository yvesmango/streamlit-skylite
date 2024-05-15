import json
from datetime import datetime
import streamlit as st
from streamlit_lottie import st_lottie
import google.auth
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas_gbq
import pandas as pd 
import geopandas as gpd
import pydeck as pdk


st.set_page_config(page_title="Streamlit: Skylite Travel Tracker", layout="wide")
    

#Create API client.
credentials = service_account.Credentials.from_service_account_info(
     st.secrets["gcp_service_account"]
 )

client = bigquery.Client(credentials=credentials)

# # Perform query
# # Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)

def run_query(query):
     query_job = client.query(query)
     rows_raw = query_job.result()
     # Convert to list of dicts. Required for st.cache_data to hash the return value.
     rows = [dict(row) for row in rows_raw]
     return rows

latest_data = "SELECT * EXCEPT (id, snippet_description) FROM data-sciencey-things.skylite_travel.flights ORDER BY snippet_publishedAt DESC"


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


airplane = load_lottiefile('./lottiefiles/airplane.json')


# Function to get current date and time
def get_current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# ## Opening dataframe
# df = (
#      client.query(latest_data).result().to_dataframe()
#  )

# Open dataframe and store it in session state
@st.cache_data(ttl=600)
def load_dataframe(query):
    df = client.query(query).result().to_dataframe()

    return df

# Store dataframe in session state
st.session_state.df = load_dataframe(latest_data)


## TOP SECTION LAYOUT

with st.container():
     
     col1, col2, col3 = st.columns((1,1,2))

     with col1:
          st.write("## Yves TRAVEL APP") 

     with col2:
          st.lottie(airplane, height=100, width=200)    

    


# st.write("#### Latest data files")
# st.write(df.sort_values(by=['snippet_publishedAt'], ascending=False))

# Display latest data files
st.write("#### Latest data files")
st.write(st.session_state.df.head().sort_values(by=['snippet_publishedAt'], ascending=False))

# Write a brief "about me" summary




# Display latest date based on snippet_publishedAt
latest_date = st.session_state.df['snippet_publishedAt'].iloc[0].strftime('%Y-%m-%d')
st.write(f"*latest data update: {latest_date}*")