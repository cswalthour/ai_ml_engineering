# libraries supporting env setup
import os, sys
from tkinter import N
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# custom modules
from utils.sp_methods import create_snowflake_session

# snowflake API connection parameters
snowflake_api_params = {
    "account": os.getenv("ACCOUNT"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "role": 'SNOWFLAKE_INTELLIGENCE_ADMIN',
    "warehouse": "COMPUTE_WH",
    "database": "DASH_CORTEX_AGENTS",
    "schema": "DATA"
}

# create snowflake session
sp_session = create_snowflake_session(snowflake_api_params, local=True, \
    grant_marketplace_imported_privileges=True, target_role="SNOWFLAKE_INTELLIGENCE_ADMIN"
)