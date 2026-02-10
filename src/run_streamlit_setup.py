# libraries supporting env setup
import os, sys
from pathlib import Path
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# custom modules
from utils.sp_methods import create_snowflake_session, run_sql_script

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
    grant_marketplace_imported_privileges=False, target_role="SNOWFLAKE_INTELLIGENCE_ADMIN"
)

# run sql script to integrate git repository
sql_path = Path(__file__).resolve().parent / "sql_scripts" / "git_integration.sql"
pat = os.getenv("pat")
if not pat:
    raise ValueError(
        "Missing GitHub PAT in environment. Add `pat=...` to your .env (or export it) before running."
    )

# Escape any single quotes (defensive); PATs typically don't contain quotes.
pat_sql = pat.replace("'", "''")

run_sql_script(
    sp_session,
    str(sql_path),
    initialize=True,
    replacements={"<your_github_pat>": pat_sql},
)