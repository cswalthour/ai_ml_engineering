import os
import sys

# import snowflake libraries
from snowflake.snowpark import *
from snowflake.ml import *
from snowflake.snowpark.exceptions import SnowparkSQLException

# method to create a snowflake session
def create_snowflake_session(account, user, role, password):

    connection_params = {
        "account": account,
        "user": user,
        "role": role,
        "password": password,
        "warehouse": "COMPUTE_WH",
        "database": "SNOWFLAKE",
        "schema": "PUBLIC"

    }

    session = Session.builder.configs(connection_params).create()

    print(f"Snowflake session created for {user}@{account}\n")

    return session

# method to check if a stage exists
def stage_exists(session, stage_name, schema_name=None, database_name=None):
    """
    Check if a stage exists using SHOW STAGES command
    
    Args:
        session: Snowpark session object
        stage_name: Name of the stage to check
        schema_name: Optional schema name (if not current schema)
        database_name: Optional database name (if not current database)
    
    Returns:
        bool: True if stage exists, False otherwise
    """
    try:
        # Build the SHOW STAGES command
        if database_name and schema_name:
            show_cmd = f"SHOW STAGES IN {database_name}.{schema_name}"
        elif schema_name:
            show_cmd = f"SHOW STAGES IN SCHEMA {schema_name}"
        else:
            show_cmd = "SHOW STAGES"
        
        # Execute the command and collect results
        stages_df = session.sql(show_cmd).collect()
        
        # Check if stage exists in the results
        for row in stages_df:
            if row['name'].upper() == stage_name.upper():
                return True
        return False
        
    except Exception as e:
        print(f"Error checking stage existence: {e}")
        return False

# method to run sql scripts
def run_sql_script(session, script, stage_name, schema_name, database_name):

    # Read the SQL file
    with open(script, "r") as f:
        sql_text = f.read()

    # Split statements on semicolons (naive split, but works here)
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]

    if not stage_exists(session, "docs", schema_name, database_name):
    
        # Execute each statement
        for stmt in statements:
            try:
                print(f"Running: {stmt[:80]}...\n")  # preview
                session.sql(stmt).collect()
            except Exception as e:
                print(f"Error running statement: {stmt[:80]}... \n{e}\n")

    else:
        
        print(f"Stage {stage_name.upper()} already exists\n")

# method to read/process the pds using AI_PARSE_DOCUMENT
def read_process_pdfs(session, db_name, schema_name, stage_name):

    # sql to read/process the pds using AI_PARSE_DOCUMENT
    sql_ai_parse_document = f'''

    CREATE OR REPLACE TEMPORARY TABLE {db_name}.{schema_name}.RAW_TEXT AS

    SELECT RELATIVE_PATH
        ,TO_VARCHAR(AI_PARSE_DOCUMENT(to_file(file_url), {{'mode': 'layout'}}):content) AS EXTRACTED_LAYOUT 
        FROM DIRECTORY(@{db_name}.{schema_name}.{stage_name.upper()}) 
        WHERE RELATIVE_PATH LIKE '%.pdf';
        
    '''

    # execute sql script
    session.sql(sql_ai_parse_document).collect()

# method to create table that will be used by Cortex Search service as a 
# tool for Cortex Agents in order to retrieve information from PDF and JPEG files
def chunk_text_data(session, db_name, schema_name):

    sql_create_docs_chunks_table = f'''

        CREATE OR REPLACE TABLE {db_name}.{schema_name}.DOCS_CHUNKS_TABLE (
    
            RELATIVE_PATH VARCHAR(16777216), -- Relative path to the PDF file
            CHUNK VARCHAR(16777216), -- Piece of text
            CHUNK_INDEX INTEGER, -- Index for the text
            CATEGORY VARCHAR(16777216) -- Will hold the document category to enable filtering
        );
    '''
    # execute sql script
    session.sql(sql_create_docs_chunks_table).collect()

    print(f"Table {db_name}.{schema_name}.DOCS_CHUNKS_TABLE created\n")

    # sql to flatten pdf and jpg text data into chunks that will be used by Cortex Search service for embedding and indexing
    sql_insert_docs_chunks_table = f'''

        INSERT INTO {db_name}.{schema_name}.DOCS_CHUNKS_TABLE (relative_path, chunk, chunk_index, category)

        SELECT relative_path
            , chunk
            , chunk_index
            , category 
            FROM {db_name}.{schema_name}.RAW_TEXT
            -- split the text into chunks (similar to cross join)
            LATERAL FLATTEN(input => SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER (
                EXTRACTED_LAYOUT, -- full document text
                'markdown', -- format type
                1512, -- target chunk size
                256, -- overlap between chunks
                ['\n\n', '\n', ' ', '']
            )) c
    '''

    # doc string to understand SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER
    # https://docs.snowflake.com/en/sql-reference/functions/split_text_recursive_character.html

    """
    SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(text, format_type, target_chunk_size, overlap, delimiters)

    text: The text to split into chunks.
    format_type: The format type of the text.
    target_chunk_size: The target size of the chunks. (most embeddings work best with 200-400 words, small enough for precise mathcing)
    overlap: The overlap between chunks. (minimize context loss, better retrieval performance, continuity for follow-up questions)
    delimiters: The delimiters to use to split the text. (space, newline, etc.)

    """

    # execute sql script
    session.sql(sql_insert_docs_chunks_table).collect()

    print(f"Table {db_name}.{schema_name}.DOCS_CHUNKS_TABLE populated\n")

# method to orchestrate setup of Cortex Analyst and Cortex Search
def orchestrate_cortex_setup(session, db_name, schema_name, stage_name):

    try:
    
        # determine if temporary table exists; create if not
        if session.sql(f"SELECT COUNT(*) FROM {db_name}.{schema_name}.RAW_TEXT").collect()[0][0] > 0:

            print(f"Temporary table {db_name}.{schema_name}.RAW_TEXT already exists\n")

    except SnowparkSQLException as e:
        
        print(f"Error orchestrating Cortex setup: {e}\n")

        read_process_pdfs(session, db_name, schema_name, stage_name)

        sql_test = f'''

            SELECT * FROM {db_name}.{schema_name}.RAW_TEXT limit 5

        '''

        print(f"Temporary table {db_name}.{schema_name}.RAW_TEXT created:\n")

        print(session.sql(sql_test).collect())

    # create table that will be used by Cortex Search service as a 
    # tool for Cortex Agents in order to retrieve information from PDF and JPEG files
    create_insert_docs_chunks_table(session, db_name, schema_name)
        