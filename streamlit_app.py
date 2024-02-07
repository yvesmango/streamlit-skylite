import json
import streamlit as st
#from streamlit_lottie import st_lottie
import google.auth
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas_gbq
import pandas as pd 




st.set_page_config(page_title="Streamlit: Skylite Travel Tracker", layout="wide")
    

#Create API client.
credentials = service_account.Credentials.from_service_account_info(
     st.secrets["gcp_service_account"]
 )

client = bigquery.Client(credentials=credentials)
# # Perform query.
# # Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)

def run_query(query):
     query_job = client.query(query)
     rows_raw = query_job.result()
     # Convert to list of dicts. Required for st.cache_data to hash the return value.
     rows = [dict(row) for row in rows_raw]
     return rows

latest_data = "SELECT * FROM data-sciencey-things.skylite_travel.flights ORDER BY snippet_publishedAt DESC LIMIT 5"


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


airplane = load_lottiefile('./lottiefiles/airplane.json')

df = (
     client.query(latest_data).result().to_dataframe()
 )


## TOP SECTION LAYOUT

col1, col2, col3 = st.columns((3,1,1))

with col1:
     st.write("# Yves TRAVEL APP") 

with col2:
     #st.lottie(airplane, height=200, width=200)


st.write("#### Latest data files")
st.write(df.sort_values(by=['snippet_publishedAt'], ascending=False))

