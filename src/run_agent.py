from dotenv import load_dotenv
import os
from utils.sp_methods import create_snowflake_session
from utils.cortex_setup import run_sql_script, orchestrate_cortex_setup

# load environment variables
load_dotenv()

# snowpark API connection parameters
sp_params = {
    "account": os.getenv("ACCOUNT"),
    "user": os.getenv("USER"),
    "role": 'ACCOUNTADMIN',
    "password": os.getenv("PASSWORD"),
    "warehouse": "COMPUTE_WH",
    "database": "SNOWFLAKE",
    "schema": "PUBLIC"
}

# create snowflake session
sp_session = create_snowflake_session(sp_params)

# dictionary of snowflake objects
snowflake_objects = {
    "stage_name": "docs",
    "schema_name": "data",
    "db_name": "dash_cortex_agents"
}

# run sql script
run_sql_script(sp_session, "../setup.sql", snowflake_objects)

# orchestrate setup of Cortex Analyst and Cortex Search
orchestrate_cortex_setup(
    sp_session, 
    snowflake_objects["db_name"], 
    snowflake_objects["schema_name"], 
    snowflake_objects["stage_name"]
)

# close snowflake session
sp_session.close()