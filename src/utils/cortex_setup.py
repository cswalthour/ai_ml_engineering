import os
import sys

# import snowflake libraries
from snowflake.snowpark import *
from snowflake.ml import *
from snowflake.snowpark.exceptions import SnowparkSQLException

# method to check if a stage exists
def stage_exists(session, snowflake_objects):
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

    # derive database and schema from snowflake_objects
    db_name = snowflake_objects["db_name"]
    sch_name = snowflake_objects["schema_name"]
    stg_name = snowflake_objects["stage_name"]

    try:
        # Build the SHOW STAGES command
        if db_name and sch_name:
            show_cmd = f"SHOW STAGES IN {db_name}.{sch_name}"
        elif sch_name:
            show_cmd = f"SHOW STAGES IN SCHEMA {sch_name}"
        else:
            show_cmd = "SHOW STAGES"
        
        # Execute the command and collect results
        stages_df = session.sql(show_cmd).collect()
        
        # Check if stage exists in the results
        for row in stages_df:
            if row['name'].upper() == stg_name.upper():
                return True
        return False
        
    except Exception as e:
        print(f"Error checking stage existence: {e}")
        return False

# method to run sql scripts
def run_sql_script(session, script_path, snowflake_objects: dict):

    # derive database and schema from snowflake_objects
    db_name = snowflake_objects["db_name"]
    sch_name = snowflake_objects["schema_name"]
    stg_name = snowflake_objects["stage_name"]
    
    # Read the SQL file
    with open(script_path, "r") as f:
        sql_text = f.read()

    # Split statements on semicolons (naive split, but works here)
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]

    if not stage_exists(session, snowflake_objects):
    
        # Execute each statement
        for stmt in statements:
            try:
                print(f"Running: {stmt[:80]}...\n")  # preview
                session.sql(stmt).collect()
            except Exception as e:
                print(f"Error running statement: {stmt[:80]}... \n{e}\n")

    else:
        
        print(f"Stage {stg_name.upper()} already exists\n")

# method to read/process the pds using AI_PARSE_DOCUMENT
def read_process_pdfs(session, snowflake_objects: dict):

    # derive database and schema from snowflake_objects
    db_name = snowflake_objects["db_name"]
    sch_name = snowflake_objects["schema_name"]
    stg_name = snowflake_objects["stage_name"]
    role = snowflake_objects["role"]

    # set role
    session.use_role(role)

    # sql to read/process the pds using AI_PARSE_DOCUMENT
    sql_ai_parse_document = f'''

    CREATE OR REPLACE TEMPORARY TABLE {db_name}.{sch_name}.RAW_TEXT AS

    SELECT RELATIVE_PATH
        ,TO_VARCHAR(AI_PARSE_DOCUMENT(to_file(file_url), {{'mode': 'layout'}}):content) AS EXTRACTED_LAYOUT 
        FROM DIRECTORY(@{db_name}.{sch_name}.{stg_name.upper()}) 
        WHERE RELATIVE_PATH LIKE '%.pdf';
        
    '''

    # execute sql script
    session.sql(sql_ai_parse_document).collect()

    # sql to preview the data
    sql_preview_data = f'''
        SELECT * FROM {db_name}.{sch_name}.RAW_TEXT limit 5
    '''

    # preview the data
    print(f"Preview of {db_name}.{sch_name}.RAW_TEXT:\n")
    print("------------------------------------------------------------------------------------------------\n")
    session.sql(sql_preview_data).show()

# method to create table that will be used by Cortex Search service as a 
# tool for Cortex Agents in order to retrieve information from PDF and JPEG files
def chunk_text_data(session, snowflake_objects: dict):

    # derive database and schema from snowflake_objects
    db_name = snowflake_objects["db_name"]
    sch_name = snowflake_objects["schema_name"]
    stg_name = snowflake_objects["stage_name"]
    role = snowflake_objects["role"]

    # set role
    session.use_role(role)

    sql_create_docs_chunks_table = f'''

        CREATE OR REPLACE TABLE {db_name}.{sch_name}.DOCS_CHUNKS_TABLE (
    
            RELATIVE_PATH VARCHAR(16777216), -- Relative path to the PDF file
            CHUNK VARCHAR(16777216), -- Piece of text
            CHUNK_INDEX INTEGER, -- Index for the text
            CATEGORY VARCHAR(16777216) -- Will hold the document category to enable filtering
        );
    '''
    # execute sql script
    session.sql(sql_create_docs_chunks_table).collect()

    print(f"Table {db_name}.{sch_name}.DOCS_CHUNKS_TABLE created\n")

    # sql to flatten pdf and jpg text data into chunks that will be used by Cortex Search service for embedding and indexing
    sql_insert_docs_chunks_table = f'''

        INSERT INTO {db_name}.{sch_name}.DOCS_CHUNKS_TABLE (relative_path, chunk, chunk_index)
        
        select relative_path, 
                c.value::TEXT as chunk,
                c.INDEX::INTEGER as chunk_index
            FROM {db_name}.{sch_name}.RAW_TEXT,
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

    print(f"Table {db_name}.{sch_name}.DOCS_CHUNKS_TABLE populated\n")

    # test sql to preview the data
    sql_test = f'''
        SELECT * FROM {db_name}.{sch_name}.DOCS_CHUNKS_TABLE limit 5
    '''
    print(f"Preview of {db_name}.{sch_name}.DOCS_CHUNKS_TABLE:\n")
    print("------------------------------------------------------------------------------------------------\n")
    print(session.sql(sql_test).collect())

# method to test ai_classify function
def test_ai_classify(session, db_name, schema_name):
    
    # test if doc_chunks_table has category column
    sql_test_category_column = f'''

        SELECT * FROM {db_name}.{schema_name}.DOCS_CHUNKS_TABLE limit 5

    '''

    # convert to pandas dataframe
    df_category_column = session.sql(sql_test_category_column).to_pandas()

    if 'CATEGORY' not in df_category_column.columns:

        print(f"Category column not found in {db_name}.{schema_name}.DOCS_CHUNKS_TABLE\n")

        # boolean to check if category column exists
        classify_exists = False

    else:

        print(f"Category column found in {db_name}.{schema_name}.DOCS_CHUNKS_TABLE\n")

        # boolean to check if category column exists
        classify_exists = True

    # if category column does not exist, create the temp table and classify the data
    if not classify_exists:

        sql_test_ai_classify = f'''
            
            CREATE OR REPLACE TEMPORARY TABLE {db_name}.{schema_name}.docs_categories AS 
            
            WITH unique_documents AS (

                SELECT DISTINCT 
                    relative_path
                    , chunk
                    FROM {db_name}.{schema_name}.DOCS_CHUNKS_TABLE
                    WHERE chunk_index = 0
                ),

                docs_category_cte AS (
                    SELECT
                        relative_path,
                        AI_CLASSIFY(chunk, ['Bike', 'Snow']):labels[0] AS category
                    FROM
                        unique_documents
                )
                SELECT
                    *
                    FROM
                    docs_category_cte
                ;


        '''
        print(f"Creating Temp Table {db_name}.{schema_name}.DOCS_CHUNKS_TABLE:\n")
        print("------------------------------------------------------------------------------------------------\n")
        print(session.sql(sql_test_ai_classify).collect())
        
        sql_test = f'''
            SELECT * FROM {db_name}.{schema_name}.docs_categories limit 5
        '''

        session.sql(sql_test).show()

        # sql to update the chunks table with the categories
        sql_update_chunks_table = f'''

            UPDATE {db_name}.{schema_name}.DOCS_CHUNKS_TABLE
            SET category = docs_categories.category
                FROM {db_name}.{schema_name}.docs_categories
            WHERE {db_name}.{schema_name}.DOCS_CHUNKS_TABLE.relative_path = {db_name}.{schema_name}.docs_categories.relative_path

        '''

        # deploy the update
        session.sql(sql_update_chunks_table).collect()

        print(f"Table {db_name}.{schema_name}.DOCS_CHUNKS_TABLE updated with the categories:\n")

        # test sql to preview the data
        sql_test = f'''
            SELECT * FROM {db_name}.{schema_name}.DOCS_CHUNKS_TABLE limit 5
        '''

        session.sql(sql_test).show()

# method to orchestrate setup of Cortex Analyst and Cortex Search
def orchestrate_cortex_setup(session, db_name, schema_name, stage_name):

    # check to see if chunks table exists
    try:

        if session.sql(f"SELECT COUNT(*) FROM {db_name}.{schema_name}.DOCS_CHUNKS_TABLE").collect()[0][0] > 0:

            table_exists = True
            
            print(f"Table {db_name}.{schema_name}.DOCS_CHUNKS_TABLE already exists\n")

        else:

            table_exists = False

            print(f"Table {db_name}.{schema_name}.DOCS_CHUNKS_TABLE does not exist\n")

    except SnowparkSQLException as e:

        table_exists = False
        
        print(f"Error orchestrating Cortex setup: {e}\n")

    # if table does not exist, read/process the pdfs and create the chunks table
    if not table_exists:

        # preparing temp table for Cortex Split Text Recursive Character function
        read_process_pdfs(session, db_name, schema_name, stage_name)

        # test sql to preview the data
        sql_test = f'''

            SELECT * FROM {db_name}.{schema_name}.RAW_TEXT limit 5

        '''

        # test sql to preview the data
        print(f"Temporary table {db_name}.{schema_name}.RAW_TEXT created:\n")

        # show the data
        session.sql(sql_test).show()

        # apply split text recursive character function to the data
        # tool for Cortex Agents in order to retrieve information from PDF and JPEG files
        chunk_text_data(session, db_name, schema_name)
    
    # test ai_classify function to classify the data (pass doc title and first chunk of the document to the function)
    test_ai_classify(session, db_name, schema_name)
        