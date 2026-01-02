from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

# method to create dim_article table for Cortex Agents
def create_dim_article_table(session: Session):

    # fetch db/schema from session
    db_name = session.get_current_database()
    sch_name = session.get_current_schema()

    # doc string to explain DIM_ARTICLE table
    """
    DIM_ARTICLE table:
    - ARTICLE_ID: Unique identifier for each article
    - ARTICLE_NAME: Full name/description of the product
    - ARTICLE_CATEGORY: Product category (e.g., Bike, Skis, Ski Boots)
    - ARTICLE_BRAND: Manufacturer or brand (e.g., Mondracer, Carver)
    - ARTICLE_COLOR: Dominant color for the article
    - ARTICLE_PRICE: Standard unit price of the article
    """

    # sql to create DIM_ARTICLE table
    sql_create_dim_article_table = f'''

    CREATE OR REPLACE TABLE DIM_ARTICLE (
        ARTICLE_ID INT PRIMARY KEY,
        ARTICLE_NAME STRING,
        ARTICLE_CATEGORY STRING,
        ARTICLE_BRAND STRING,
        ARTICLE_COLOR STRING,
        ARTICLE_PRICE FLOAT
    );

    '''

    # execute sql script
    session.sql(sql_create_dim_article_table).collect()

    print(f"Table {db_name}.{sch_name}.DIM_ARTICLE created\n")

    # sql to insert data into DIM_ARTICLE table
    sql_insert_dim_article_table = f'''

        INSERT INTO {db_name}.{sch_name}.DIM_ARTICLE (
        ARTICLE_ID, ARTICLE_NAME, ARTICLE_CATEGORY, ARTICLE_BRAND, 
        ARTICLE_COLOR, ARTICLE_PRICE) VALUES 
        (1, 'Mondracer Infant Bike', 'Bike', 'Mondracer', 'Red', 3000),
        (2, 'Premium Bicycle', 'Bike', 'Veloci', 'Blue', 9000),
        (3, 'Ski Boots TDBootz Special', 'Ski Boots', 'TDBootz', 'Black', 600),
        (4, 'The Ultimate Downhill Bike', 'Bike', 'Graviton', 'Green', 10000),
        (5, 'The Xtreme Road Bike 105 SL', 'Bike', 'Xtreme', 'White', 8500),
        (6, 'Carver Skis', 'Skis', 'Carver', 'Orange', 790),
        (7, 'Outpiste Skis', 'Skis', 'Outpiste', 'Yellow', 900),
        (8, 'Racing Fast Skis', 'Skis', 'RacerX', 'Blue', 950);

    '''

    # execute sql script
    session.sql(sql_insert_dim_article_table).collect()

    print(f"Table {db_name}.{sch_name}.DIM_ARTICLE populated\n")

# method to create dim_customer table for Cortex Agents
def create_dim_customer_table(session: Session):

    # fetch db/schema from session
    db_name = session.get_current_database()
    sch_name = session.get_current_schema()

    # doc string to explain DIM_CUSTOMER table
    """
    DIM_CUSTOMER table:
    - CUSTOMER_ID: Unique identifier for each customer
    - CUSTOMER_NAME: Display name for the customer
    - CUSTOMER_REGION: Geographic region where the customer is located
    - CUSTOMER_AGE: Age of the customer
    - CUSTOMER_GENDER: Gender of the customer
    - CUSTOMER_SEGMENT: Marketing segment of the customer
    """

    # sql to create DIM_CUSTOMER table
    sql_create_dim_customer_table = f'''

        CREATE OR REPLACE TABLE DIM_CUSTOMER (
            CUSTOMER_ID INT PRIMARY KEY,
            CUSTOMER_NAME STRING,
            CUSTOMER_REGION STRING,
            CUSTOMER_AGE INT,
            CUSTOMER_GENDER STRING,
            CUSTOMER_SEGMENT STRING
        );

    '''

    # execute sql script
    session.sql(sql_create_dim_customer_table).collect()

    print(f"Table {db_name}.{sch_name}.DIM_CUSTOMER created\n")

    # sql to insert data into DIM_CUSTOMER table
    sql_insert_dim_customer_table = f'''

        INSERT INTO {db_name}.{sch_name}.DIM_CUSTOMER (
            CUSTOMER_ID,
            CUSTOMER_NAME,
            CUSTOMER_REGION,
            CUSTOMER_AGE,
            CUSTOMER_GENDER,
            CUSTOMER_SEGMENT
        )
        WITH base AS (
            SELECT SEQ4() + 1 AS customer_id
            FROM TABLE(GENERATOR(ROWCOUNT => 5000))
        )
        SELECT
            customer_id,
            'Customer ' || customer_id AS customer_name,
            CASE MOD(customer_id, 5)
                WHEN 0 THEN 'North'
                WHEN 1 THEN 'South'
                WHEN 2 THEN 'East'
                WHEN 3 THEN 'West'
                ELSE 'Central'
            END AS customer_region,
            UNIFORM(18, 65, RANDOM()) AS customer_age,
            CASE MOD(customer_id, 2)
                WHEN 0 THEN 'Male'
                ELSE 'Female'
            END AS customer_gender,
            CASE MOD(customer_id, 3)
                WHEN 0 THEN 'Premium'
                WHEN 1 THEN 'Regular'
                ELSE 'Occasional'
            END AS customer_segment
        FROM base;

    '''

    # execute sql script
    session.sql(sql_insert_dim_customer_table).collect()

    print(f"Table {db_name}.{sch_name}.DIM_CUSTOMER populated\n")

# method to create fact_sales table for Cortex Agents
def create_fact_sales_table(session: Session):

    # fetch db/schema from session
    db_name = session.get_current_database()
    sch_name = session.get_current_schema()

    # doc string to explain FACT_SALES table
    """
    FACT_SALES table:
    - SALE_ID: Unique identifier for each sale  
    - ARTICLE_ID: Unique identifier for each article
    - DATE_SALES: Date when the sale occurred
    - CUSTOMER_ID: Unique identifier for each customer
    - QUANTITY_SOLD: Number of units sold in the transaction
    - TOTAL_PRICE: Total transaction value (unit price × quantity)
    - SALES_CHANNEL: Sales channel used (e.g., Online, In-Store, Partner)
    - PROMOTION_APPLIED: Boolean indicating if the sale involved a promotion or discount
    - FOREIGN KEY (ARTICLE_ID) REFERENCES DIM_ARTICLE(ARTICLE_ID)
    - FOREIGN KEY (CUSTOMER_ID) REFERENCES DIM_CUSTOMER(CUSTOMER_ID)
    """

    # sql to create FACT_SALES table
    sql_create_fact_sales_table = f'''

        CREATE OR REPLACE TABLE FACT_SALES (
            SALE_ID INT PRIMARY KEY,
            ARTICLE_ID INT,
            DATE_SALES DATE,
            CUSTOMER_ID INT,
            QUANTITY_SOLD INT,
            TOTAL_PRICE FLOAT,
            SALES_CHANNEL STRING,
            PROMOTION_APPLIED BOOLEAN,
            FOREIGN KEY (ARTICLE_ID) REFERENCES DIM_ARTICLE(ARTICLE_ID),
            FOREIGN KEY (CUSTOMER_ID) REFERENCES DIM_CUSTOMER(CUSTOMER_ID)
        );

    '''

    # execute sql script
    session.sql(sql_create_fact_sales_table).collect()

    print(f"Table {db_name}.{sch_name}.FACT_SALES created\n")

    # sql to insert data into FACT_SALES table
    sql_insert_fact_sales_table = f'''  

        -- Populating Sales Fact Table with new attributes
        INSERT INTO {db_name}.{sch_name}.FACT_SALES (
            SALE_ID,
            ARTICLE_ID,
            DATE_SALES,
            CUSTOMER_ID,
            QUANTITY_SOLD,
            TOTAL_PRICE,
            SALES_CHANNEL,
            PROMOTION_APPLIED
        )
        WITH gen AS (
            SELECT
                SEQ4() + 1 AS sale_id,
                UNIFORM(1, 8, RANDOM())::INT AS article_id,
                DATEADD(DAY, UNIFORM(-1095, 0, RANDOM()), CURRENT_DATE) AS date_sales,
                UNIFORM(1, 5000, RANDOM())::INT AS customer_id,
                UNIFORM(1, 10, RANDOM())::INT AS quantity_sold,
                CASE MOD(SEQ4(), 3)
                    WHEN 0 THEN 'Online'
                    WHEN 1 THEN 'In-Store'
                    ELSE 'Partner'
                END AS sales_channel,
                CASE MOD(SEQ4(), 4)
                    WHEN 0 THEN TRUE
                    ELSE FALSE
                END AS promotion_applied
            FROM TABLE(GENERATOR(ROWCOUNT => 10000))
        )
        SELECT
            g.sale_id,
            g.article_id,
            g.date_sales,
            g.customer_id,
            g.quantity_sold,
            (g.quantity_sold * a.article_price)::FLOAT AS total_price,
            g.sales_channel,
            g.promotion_applied
        FROM gen g
        JOIN {db_name}.{sch_name}.DIM_ARTICLE a
          ON a.article_id = g.article_id;

    '''

    # execute sql script
    session.sql(sql_insert_fact_sales_table).collect()

    print(f"Table {db_name}.{sch_name}.FACT_SALES populated\n")

# method to check if table exists
def table_exists(session: Session, table_name: str):

    # fetch db/schema from session
    db_name = session.get_current_database()
    sch_name = session.get_current_schema()

    try:
        # `get_current_database/schema()` may return quoted identifiers like '"DB"'.
        # Do NOT replace quotes with single quotes (that produces invalid identifiers).
        db = db_name.strip('"') if db_name else db_name
        sch = sch_name.strip('"') if sch_name else sch_name

        # SHOW TABLES returns 0 rows if the table doesn't exist.
        sql = f"SHOW TABLES LIKE '{table_name}' IN SCHEMA {db}.{sch}"
        result = session.sql(sql).collect()

        if len(result) > 0:
            print(f"Table {db}.{sch}.{table_name} exists\n")
            return True

        print(f"Table {db}.{sch}.{table_name} does not exist\n")
        return False

    except SnowparkSQLException as e:
        print(f"Error checking if table exists: {e}\n")
        print(f"Table {db_name}.{sch_name}.{table_name} does not exist\n")
        return False

# method to create supporting tables for Cortex Agents
def create_supporting_tables(session: Session, table_name: str):

    # fetch db/schema from session
    db_name = session.get_current_database()
    sch_name = session.get_current_schema()

    # check if table exists and create it if it doesn't
    if not table_exists(session, table_name):

        if table_name == 'DIM_ARTICLE':
            create_dim_article_table(session)
        elif table_name == 'DIM_CUSTOMER':
            create_dim_customer_table(session)
        else:
            create_fact_sales_table(session)
