import os
import sys
from pathlib import Path

# import snowflake libraries
from snowflake.snowpark import *
from snowflake.ml import *
from snowflake.snowpark.exceptions import SnowparkSQLException

# method to create a snowflake session
def create_snowflake_session(
    sp_params: dict,
    local: bool = False,
    *,
    grant_marketplace_imported_privileges: bool = False,
    marketplace_databases: list[str] | None = None,
    target_role: str | None = None,
):
    """
    Create a Snowpark session.

    Notes on Snowflake Marketplace / shared databases:
    - Marketplace listings are installed into your account as shared databases.
    - To allow a role to access them, an admin typically runs:
        GRANT IMPORTED PRIVILEGES ON DATABASE <db> TO ROLE <role>;
    - This requires appropriate privileges (e.g., ACCOUNTADMIN / MANAGE GRANTS).

    By default, this function does NOT attempt to grant imported privileges because:
    - it's not always permitted for the connecting role, and
    - session creation should not fail due to an optional admin step.
    """

    if marketplace_databases is None:
        marketplace_databases = ["SNOWFLAKE_PUBLIC_DATA_FREE", "SNOWFLAKE_PUBLIC_DATA_FOREIGN_EXCHANGE_RATES"]


    # create session for local development
    if local:

        print("Creating session for local development...\n")

        session = Session.builder.configs(sp_params).create()

        # Optionally grant imported privileges for Marketplace/shared databases.
        if grant_marketplace_imported_privileges:

            # ensure that ACCOUNTADMIN role is used
            if sp_params["role"] != "ACCOUNTADMIN":
                
                session.use_role("ACCOUNTADMIN")

            # print target role
            print(f"Target role: {target_role}\n")

            # raise error if target role is none
            if target_role is None:
                raise ValueError("target_role is required when grant_marketplace_imported_privileges=True")

            # grant imported privileges for each database
            for db in marketplace_databases:

                # sql to grant imported privileges
                sql_grant = f"GRANT IMPORTED PRIVILEGES ON DATABASE {db} TO ROLE {target_role}"
                try:
                    session.sql(sql_grant).collect()
                except SnowparkSQLException as e:
                    print(
                        f"Warning: failed to grant imported privileges for database {db} to role "
                        f"{target_role}: {e}"
                    )

            # switch role to target role
            session.use_role(target_role)

        # derive user and account from sp_params
        user = sp_params["user"]
        account = sp_params["account"]

        # print role used
        print(f"Role used: {session.get_current_role()}\n")

        # print session created message
        print(f"Snowflake session created for {user}@{account}\n")

    # create session for remote development
    else:

        session = Session.builder.get_active_session()

        # fetch user and account from session
        user = session.get_current_user()
        account = session.get_current_account()

        # print role used
        print(f"Role used: {session.get_current_role()}\n")

        # print session created message
        print(f"Snowflake session created for {user}@{account}\n")

    # return session
    return session

# method to run a sql script
def run_sql_script(
    session,
    sql_script_path: str,
    initialize: bool = False,
    *,
    replacements: dict[str, str] | None = None,
):
    """
    Run a SQL script.
    """
    # raise error if initialize is True and sql_script_path is None
    if initialize and sql_script_path is None:
        raise ValueError("sql_script_path is required when initialize=True")

    # if initialize is True, run the sql script
    if initialize:

        # fetch current role
        current_role = session.get_current_role()

        # change to ACCOUNTADMIN role
        session.use_role("ACCOUNTADMIN")

        # print role used
        print(f"Role used: {session.get_current_role()}\n")

        # resolve path (so it works regardless of current working directory)
        path = Path(sql_script_path).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()

        # read the sql script
        with open(path, "r", encoding="utf-8") as file:
            sql_script = file.read()

        # Apply simple string replacements (e.g., inject secrets from env at runtime).
        if replacements:
            for old, new in replacements.items():
                sql_script = sql_script.replace(old, new)

        # split statements on semicolons (naive split, but OK for these scripts)
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

        # execute statements one-by-one
        for stmt in statements:
            print(f"Running: {stmt}...\n")  # preview
            session.sql(stmt).collect()

        # switch back to original role
        session.use_role(current_role)