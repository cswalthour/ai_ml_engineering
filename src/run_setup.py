from dotenv import load_dotenv
import os
from utils.sp_methods import create_snowflake_session
from utils.cortex_setup import run_sql_script, read_process_pdfs
from utils.cortex_setup import create_chunk_table, check_image_processing

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
    "schema": "PUBLIC",
    "initialize": False
}

# create snowflake session
sp_session = create_snowflake_session(sp_params)

# dictionary of snowflake objects
snowflake_objects = {
    "stage_name": "docs",
    "schema_name": "data",
    "db_name": "dash_cortex_agents"
}

# initialize snowflake session
if sp_params["initialize"] == True:

    print("Initializing Snowflake session for object setup...\n")

    # run sql script
    run_sql_script(sp_session, "../setup.sql", snowflake_objects)

    print("Object setup complete...\n")

# add key-pair to snowflake_objects
snowflake_objects["role"] = "SNOWFLAKE_INTELLIGENCE_ADMIN"

# read/process the pdfs
read_process_pdfs(sp_session, snowflake_objects)

# create chunk table and classify the text data
create_chunk_table(sp_session, "DOCS_CHUNKS_TABLE")

# process the images for description using AI_COMPLETE function
check_image_processing(sp_session, snowflake_objects)

# close snowflake session
sp_session.close()