import requests
from requests.auth import HTTPBasicAuth
import csv
import os
from dotenv import load_dotenv
import pandas as pd
from snowflake.snowpark import Session
from utils.confl_views import fetch_view_counts, ensure_latest_packages, extract_labels
from datetime import datetime

load_dotenv()

# get environment variables
api_token = os.getenv("CONFL")

# -----------------------------
# Config
# -----------------------------
BASE_URL = "https://jirapp.atlassian.net/wiki/rest/api/content"
SPACE_KEY = "DNA"  # Replace with your Confluence space key
USERNAME = "christopher.walthour@patientpoint.com"
PAGE_URL = "https://jirapp.atlassian.net/wiki/spaces/DNA/pages"
ANALYTICS_URL = "https://jirapp.atlassian.net/wiki/rest/api/analytics/content"


# # REST API endpoint to get content from a space
# url = f"{BASE_URL}/rest/api/space/{SPACE_KEY}/content"

# # Make request with authentication
# resp = requests.get(
#     url,
#     auth=HTTPBasicAuth(USERNAME, api_token),
#     headers={"Accept": "application/json"}
# )

# if resp.status_code == 200:
#     data = resp.json()
#     for page in data.get("page", {}).get("results", []):
#         print(f"Title: {page['title']} | ID: {page['id']}")
# else:
#     print(f"Error {resp.status_code}: {resp.text}")


# -----------------------------
# Setup authentication
# -----------------------------
auth = (USERNAME, api_token)

# Expand fields for content manager data
expand = "history,version,metadata"

# -----------------------------
# Get paginated results
# -----------------------------
results = []
start = 0
limit = 50

# start time
start_time = datetime.now()
print(f"Start time: {start_time}")

while True:
    url = f"{BASE_URL}?spaceKey={SPACE_KEY}&expand={expand}&limit={limit}&start={start}"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()

    data = resp.json()
    results.extend(data.get("results", []))

    # Check for next page
    if "_links" in data and "next" in data["_links"]:
        start += limit
    else:
        break

print(f"Fetched {len(results)} content items")

# Build list of dicts from results
data_results = []
views_results = []
labels_results = []

for i,r in enumerate(results):

    print(f"Processing {i+1} of {len(results)}")

    # extracting metadata from content json
    data_results.append({
        "id": r.get("id"),
        "title": r.get("title"),
        "type": r.get("type"),
        "space_key": r.get("space", {}).get("key"),
        "created_by": r.get("history", {}).get("createdBy", {}).get("displayName"),
        "created_date": r.get("history", {}).get("createdDate"),
        "last_updated_by": r.get("version", {}).get("by", {}).get("displayName"),
        "last_updated_date": r.get("version", {}).get("when"),
        "version": r.get("version", {}).get("number"),
        # "labels": ",".join(
        #     [l["name"] for l in r.get("metadata", {}).get("labels", {}).get("results", [])]
        # ),
        "url": f'{PAGE_URL}/{r.get("id")}'
    })

    # fetching view counts per page
    views_data = fetch_view_counts(ANALYTICS_URL, r.get("id"), auth)
    
    # appending views data to views_results
    views_results.append(views_data)

    # fetching labels per page
    labels_data = extract_labels(r.get("id"), auth)
    labels_results.append(labels_data)

# Convert to pandas DataFrame
df_results = pd.DataFrame(data_results)
df_views = pd.DataFrame(views_results)
df_labels = pd.DataFrame(labels_results)

# merge df_results and df_views on id
df_results = df_results.merge(df_views, on="id", how="left")
df_results = df_results.merge(df_labels, on="id", how="left")

# add timestamp to df_results
df_results["datetime_content_fetched"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# end time
end_time = datetime.now()

# difference between end time and start time in minutes
time_taken = end_time - start_time
time_taken_minutes = time_taken.total_seconds() / 60

# print time taken (in minutes)
print(f"Time taken to fetch content and view counts: {time_taken_minutes} minutes")

# Show first few rows
print(f'First 5 rows of df_results:\n{df_results.head(5)}')

ADV_ANALYTICS_USER = os.getenv("ADV_ANALYTICS_USER")
ADV_ANALYTICS_PWD = os.getenv("ADV_ANALYTICS_PASSWORD")

#Snowpark API Connection parameters
connection_params = {
    "account": "patientpoint.us-east-1",
    "user": ADV_ANALYTICS_USER,
    "password": ADV_ANALYTICS_PWD,
    "warehouse":'ADV_S_WH',
    "role": 'ADV_DEPLOY_RL',
    "database": 'ADV_ANALYTICS_DEV_DB',
    "schema": 'DATA_MANAGEMENT'
}

# ensure latest packages are installed
ensure_latest_packages()

# create new snowpark session based on new config settings
new_session = Session.builder.configs(connection_params).create()

# create snowpark dataframe from df_results
df_results_snowpark = new_session.create_dataframe(df_results)

# write into snowflake table
df_results_snowpark.write.mode("overwrite").save_as_table("CONFLUENCE_CONTENT_MGR")

# close snowpark session
new_session.close()


