from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

# method to check if a stage exists
def stage_exists(session: Session, semantic_models: dict):

    # derive db/schema from session context and strip double quotes if present
    db_name_raw = session.get_current_database()
    sch_name_raw = session.get_current_schema()

    db_name = db_name_raw.strip('"') if db_name_raw else db_name_raw
    sch_name = sch_name_raw.strip('"') if sch_name_raw else sch_name_raw
    stg_name = semantic_models["stage_name"]

    # sql to check if stage exists
    sql_stage_exists = f"SHOW STAGES IN {db_name}.{sch_name}"

    result = session.sql(sql_stage_exists).collect()

    # SHOW STAGES returns a list[Row]; each row includes a "name" field.
    stage_names = {
        (row["name"] or "").upper()
        for row in result
        if "name" in row.as_dict()
    }
    exists = stg_name.upper() in stage_names

    if exists:
        print(f"Stage {db_name}.{sch_name}.{stg_name} exists\n")
        return True

    else:
        print(f"Stage {db_name}.{sch_name}.{stg_name} does not exist\n")

        # sql to create stage
        sql_create_stage = f"""
            CREATE OR REPLACE STAGE {db_name}.{sch_name}.{stg_name}
            ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
            DIRECTORY = ( ENABLE = true );
        """

        session.sql(sql_create_stage).collect()
        print(f"Stage {db_name}.{sch_name}.{stg_name} created\n")
        return False

# method to upload files to a stage
def upload_files_to_stage(session: Session, semantic_models: dict):

    # derive db/schema from semantic_models and strip double quotes if present
    db_name_raw = session.get_current_database()
    sch_name_raw = session.get_current_schema()
    db_name = db_name_raw.strip('"') if db_name_raw else db_name_raw
    sch_name = sch_name_raw.strip('"') if sch_name_raw else sch_name_raw
    
    # check if stage exists
    stage_exists(session, semantic_models)

    # upload files to stage
    for file in semantic_models["files"]:

        # upload file to stage
        session.file.put(
            local_file_name=f"{semantic_models['directory_path']}/{file}",
            stage_location=f"@{db_name}.{sch_name}.{semantic_models['stage_name']}",
            overwrite=True,
            auto_compress=False,
        )

        print(f"File {file} uploaded to stage {db_name}.{sch_name}.{semantic_models['stage_name']}\n")

    print(f"All files uploaded to stage {db_name}.{sch_name}.{semantic_models['stage_name']}\n")