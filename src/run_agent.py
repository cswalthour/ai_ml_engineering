from dotenv import load_dotenv
import os
from utils.config import create_snowflake_session, run_sql_script, orchestrate_cortex_setup

# load environment variables
load_dotenv()

# get environment variables
account = os.getenv("ACCOUNT")
user = os.getenv("USER")
role = 'ACCOUNTADMIN'
password = os.getenv("PASSWORD")

# declare variables
stage_name = "docs"
schema_name = "data"
db_name = "dash_cortex_agents"

# create snowflake session
sp_session = create_snowflake_session(account, user, role, password)

# run sql script
run_sql_script(sp_session, "../setup.sql", stage_name, schema_name, db_name)

# close snowflake session
sp_session.close()

# create snowflake session using new role
sp_session = create_snowflake_session(account, user, 'SNOWFLAKE_INTELLIGENCE_ADMIN', password)

# orchestrate setup of Cortex Analyst and Cortex Search
orchestrate_cortex_setup(sp_session, db_name, schema_name, stage_name)

# close snowflake session
sp_session.close()