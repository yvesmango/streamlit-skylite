import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas_gbq
import pandas as pd

st.set_page_config(page_title="Streamlit: Skylite Travel Tracker", layout="wide")

    


# Create API client credentials.
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])

# Perform query and read data into DataFrame using pandas.read_gbq().
def run_query(query):
    df = pd.read_gbq(query, credentials=credentials, project_id="data-sciencey-things")
    return df

# Example query
query = "SELECT * FROM `data-sciencey-things.skylite_travel.flights`"

# Call the function to run the query and get the DataFrame
df = run_query(query)