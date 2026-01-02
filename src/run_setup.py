from dotenv import load_dotenv
import os
from utils.sp_methods import create_snowflake_session

# setup dependent snowflake objects and reading from stage
from utils.cortex_setup import run_sql_script, read_process_pdfs

# creating pdf and image processing results
from utils.cortex_setup import create_chunk_table, check_image_processing

# creating Cortex Search service for the chunk table
from utils.cortex_setup import orchestrate_cortex, quantify_cortex

# creating supporting tables for Cortex Agents (DIM_ARTICLE, DIM_CUSTOMER, FACT_SALES)
from utils.semantic_tables import create_supporting_tables

# uploading files to stage in snowflake
from utils.stage_setup import upload_files_to_stage

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

# create Cortex Search service for the chunk table
orchestrate_cortex(sp_session, "DOCS")

# list of supporting tables for Cortex Agents
supporting_tables = ['DIM_ARTICLE', 'DIM_CUSTOMER', 'FACT_SALES']

# create supporting tables for Cortex Agents
for table in supporting_tables:
    create_supporting_tables(sp_session, table)

# dictionary of semantic models to upload to stage
semantic_models = {
    "directory_path": "../",
    "files": ["semantic_search.yaml", "semantic.yaml"],
    "stage_name": "SEMANTIC_FILES"
}

# upload semantic models to stage in snowflake
upload_files_to_stage(sp_session, semantic_models)

# create Cortex Search service for the article name table
orchestrate_cortex(sp_session, "ARTICLE_NAME_SEARCH")

# quantify cortex-related credit consumption
quantify_cortex(sp_session, 'DOCS')

# close snowflake session
sp_session.close()