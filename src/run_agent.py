from dotenv import load_dotenv
import os
from utils.sp_methods import create_snowflake_session
from utils.cortex_setup import run_sql_script
from utils.cortex_setup import read_process_pdfs
from utils.cortex_setup import chunk_text_data

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

# add key-pair to snowflake_objects
snowflake_objects["role"] = "SNOWFLAKE_INTELLIGENCE_ADMIN"

# run sql script
run_sql_script(sp_session, "../setup.sql", snowflake_objects)

# read/process the pdfs
read_process_pdfs(sp_session, snowflake_objects)

# chunk the text data
chunk_text_data(sp_session, snowflake_objects)

# close snowflake session
sp_session.close()