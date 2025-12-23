import os
import sys

# import snowflake libraries
from snowflake.snowpark import *
from snowflake.ml import *
from snowflake.snowpark.exceptions import SnowparkSQLException

# method to create a snowflake session
def create_snowflake_session(sp_params:dict):

    session = Session.builder.configs(sp_params).create()

    # derive user and account from sp_params
    user = sp_params["user"]
    account = sp_params["account"]

    # print session created message
    print(f"Snowflake session created for {user}@{account}\n")

    # return session
    return session