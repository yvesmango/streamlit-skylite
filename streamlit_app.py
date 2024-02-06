import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas_gbq
import pandas as pd

st.set_page_config(page_title="Streamlit: Skylite Travel Tracker", layout="wide")

    


# # Create API client credentials.
# credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])


# @st.cache_data(ttl=600)
# # Perform query and read data into DataFrame using pandas.read_gbq().
# def run_query(query):
#     df = pd.read_gbq(query, credentials=credentials, project_id="data-sciencey-things")
#     return df

# # Example query
# query = "SELECT * FROM `data-sciencey-things.skylite_travel.flights`"

# # Call the function to run the query and get the DataFrame
# df = run_query(query)

# print(df.shape)


# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

rows = run_query("SELECT * FROM `data-sciencey-things.skylite_travel.flights LIMIT 10`")


# Print results.
st.write("Some wise words from Shakespeare:")
for row in rows:
    st.write("✍️ " + row['airline'])