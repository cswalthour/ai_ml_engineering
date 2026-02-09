import os
import sys

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

        # print role used
        print(f"Role used: {session.get_current_role()}\n")

        # print session created message
        print(f"Snowflake session created for {user}@{account}\n")

    # return session
    return session