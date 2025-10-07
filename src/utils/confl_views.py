import requests
import subprocess
import os
import sys
from datetime import datetime, timedelta, timezone

# method to fetch view counts for each page
def fetch_view_counts(analytics_url, content_id, auth: tuple):

    # print(f"Fetching view counts for {content_id}")

    # define last 30 days from current date
    from_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    # define analytics url
    analytics_url = f"{analytics_url}/{content_id}/views?fromDate={from_date}"

    headers = {"Accept": "application/json"}

    resp = requests.get(analytics_url, auth=auth, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        view_count = data.get("count", 0)
    else:
        view_count = None

    views_data = {"id": content_id, "last_30_days_views": view_count}
    
    return views_data

# method to extract labels from a page
def extract_labels(content_id, auth: tuple):
    
    # define base url
    base_url = "https://jirapp.atlassian.net/wiki"
    
    # define labels url
    labels_url = f"{base_url}/rest/api/content/{content_id}/label"

    # get labels
    resp = requests.get(labels_url, auth=auth)
    resp.raise_for_status()

    labels_data = resp.json().get("results", [])
    labels = [l.get("name") for l in labels_data]

    # convert labels to string
    labels = ", ".join(labels)

    labels_data = {"id": content_id, "labels": labels}

    return labels_data

# method to ensure latest packages are installed
def ensure_latest_packages():
    """
    Ensures certifi and Snowflake packages are up-to-date.
    Executes pip install upgrade commands using subprocess.
    """
    # packages = [
    #     "certifi",
    #     "snowflake-snowpark-python",
    #     "snowflake-connector-python"
    # ]
    # for pkg in packages:
    #     print(f"🔄 Upgrading {pkg}...")
    #     subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", pkg])

    # # (Optional) Print certifi bundle location for debugging
    # import certifi
    # print(f"✅ Certifi CA bundle: {certifi.where()}")

    # subprocess.check_call([
    #     sys.executable, "-m", "pip", "install", "--upgrade",
    #     "snowflake-connector-python>=3.10.0,<4.0.0",
    #     "snowflake-snowpark-python>=1.16.0,<1.17.0",
    #     "certifi"
    # ])

    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--upgrade",
        "snowflake-connector-python",
        "snowflake-snowpark-python",
        "certifi"
    ])
