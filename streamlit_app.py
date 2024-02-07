import streamlit as st
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

query_string = "SELECT * FROM data-sciencey-things.skylite_travel.flights"

df = (
     client.query(query_string).result().to_dataframe()
 )

st.write("# Yves TRAVEL APP")
st.write(df.sort_values(by=['snippet_publishedAt'], ascending=False).head(5))

