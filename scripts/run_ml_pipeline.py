# import snowpark libraries
from snowflake.snowpark import session
from pathlib import Path

# import custom modules
from src.utils.sp_methods import create_snowflake_session, run_sql_script

# import dotenv
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# snowflake params for snowflake session
snowflake_params = {
    "account": os.getenv("TRIAL_ACCOUNT"),
    "user": os.getenv("TRIAL_USER"),
    "password": os.getenv("TRIAL_PASSWORD"),
    "role": "SNOWFLAKE_INTELLIGENCE_ADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "DASH_CORTEX_AGENTS",
    "schema": "DATA"
}

# create snowflake session
snowflake_session = create_snowflake_session(snowflake_params, local=True)

print(f"Snowflake session created for \
    {snowflake_session.get_current_user()}@{snowflake_session.get_current_account()}\n")

# project root path
root_path = Path(__file__).resolve().parent.parent

# sql script path
sql_path = root_path / "site" / "sfguides" / "src" / "cortex-code-foundations" / \
    "assets"
    
# sql script name
sql_setup_script = sql_path / "00_snowday_setup.sql"

# run sql script to create workshop env
run_sql_script(snowflake_session, str(sql_setup_script), initialize=False)

# sql load sample data script
sql_load_sample_data_script = sql_path / "00_sample_data.sql"

# run sql script to load sample data
run_sql_script(snowflake_session, str(sql_load_sample_data_script), initialize=True)