import requests
import subprocess
import os
import sys
from datetime import datetime, timedelta, timezone
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

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

# method to create snowflake view
def create_snowflake_view(session: Session, table_name: str):

    # extract db/schema from session
    db_name = session.get_current_database()
    schema_name = session.get_current_schema()
    
    # sql to create snowflake view
    sql_view = f'''

        CREATE OR REPLACE VIEW {db_name}.{schema_name}.VW_CONFLUENCE_CONTENT_MGR AS

        SELECT *
            FROM {db_name}.{schema_name}.{table_name}
            QUALIFY ROW_NUMBER() OVER(PARTITION BY "id" ORDER BY "datetime_content_fetched" DESC) = 1
            ORDER BY "created_date", "id"

    '''

    # determine if view already exists
    view_exists = session.sql(f"show views like 'ADV_ANALYTICS_DEV_DB.DATA_MANAGEMENT.VW_CONFLUENCE_CONTENT_MGR'").collect()

    if view_exists == []:

        # create view
        session.sql(sql_view).collect()

        print(f"View {db_name}.{schema_name}.VW_CONFLUENCE_CONTENT_MGR created")

    else:

        print(f"View {db_name}.{schema_name}.VW_CONFLUENCE_CONTENT_MGR already exists")

# method to write to snowflake with append/overwrite condition
def write_to_snowflake(df, table_name, connection_params, drop_table: bool = False):

    # ensure latest packages are installed for snowflake-snowpark-python
    # ensure_latest_packages()

    # create snowflake session
    sp_session = Session.builder.configs(connection_params).create()

    # add timestamp to dataframe
    df["datetime_created"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # create snowflake dataframe
    df_snowpark = sp_session.create_dataframe(df)

    # drop table if it exists
    if drop_table:

        sp_session.sql(f"drop table if exists {table_name}").collect()

    # check if table exists
    try:

        result = sp_session.table(table_name).collect()

        print(f"Table {table_name}: {result}")

        if result == []:

            table_exists = False

        else:

            table_exists = True

    except SnowparkSQLException as e:

        table_exists = False

    if table_exists:

        # append data to table
        df_snowpark.write.mode("append").save_as_table(table_name)

    else:

        # create table
        df_snowpark.write.mode("overwrite").save_as_table(table_name)

    # create snowflake view, if it doesn't exist
    create_snowflake_view(sp_session, table_name)

    # close snowflake session
    sp_session.close()
