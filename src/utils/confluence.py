import requests
from requests.auth import HTTPBasicAuth
import csv
import os
from dotenv import load_dotenv
import pandas as pd
from snowflake.snowpark import Session

load_dotenv()

# get environment variables
api_token = os.getenv("CONFL")

# -----------------------------
# Config
# -----------------------------
BASE_URL = "https://jirapp.atlassian.net/wiki/rest/api/content"
SPACE_KEY = "DNA"  # Replace with your Confluence space key
USERNAME = "christopher.walthour@patientpoint.com"


# REST API endpoint to get content from a space
url = f"{BASE_URL}/rest/api/space/{SPACE_KEY}/content"

# Make request with authentication
resp = requests.get(
    url,
    auth=HTTPBasicAuth(USERNAME, api_token),
    headers={"Accept": "application/json"}
)

if resp.status_code == 200:
    data = resp.json()
    for page in data.get("page", {}).get("results", []):
        print(f"Title: {page['title']} | ID: {page['id']}")
else:
    print(f"Error {resp.status_code}: {resp.text}")


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

for r in results:
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
        "labels": ",".join(
            [l["name"] for l in r.get("metadata", {}).get("labels", {}).get("results", [])]
        ),
    })

# Convert to pandas DataFrame
df_results = pd.DataFrame(data_results)

# Show first few rows
print(df_results.head())

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

# create new snowpark session based on new config settings
new_session = Session.builder.configs(connection_params).create()

# create snowpark dataframe from df_results
df_results_snowpark = new_session.create_dataframe(df_results)

# write into snowflake table
df_results_snowpark.write.mode("overwrite").save_as_table("CONFLUENCE_CONTENT_MGR")

# close snowpark session
new_session.close()
