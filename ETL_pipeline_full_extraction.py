from prefect import flow, task
import sqlite3
import duckdb
import pandas as pd
from datetime import datetime

# Config
SQLITE_DB_PATH = "MLED_transactions.db"
DUCKDB_PATH = "MLED_analytics.duckdb"
TABLE_NAME = "experiments"

@task
def extract_all_data() -> pd.DataFrame:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    
    query = """
    SELECT
        e.Experiment_ID,
        e.Name AS Experiment_Name,
        e.Description AS Experiment_Description,
        e.Status AS Experiment_Status,
        e.StartTimeStamp,
        e.EndTimeStamp,
        u.First_Name || ' ' || u.Last_Name AS Author_Name,
        
        d.DataSet_ID,
        d.Name AS Dataset_Name,
        d.Version AS Dataset_Version,
        d.Size AS Dataset_Size,
        d.Description AS Dataset_Description,
        
        m.Model_ID,
        m.Name AS Model_Name,
        m.Type AS Model_Type,
        m.Version AS Model_Version,
        m.Hyperparameters AS Model_Hyperparameters,

        t.Trial_ID,
        t.Status AS Trial_Status,
        t.StartTime AS Trial_Start,
        t.EndTime AS Trial_End,
        t.Seed AS Trial_Seed,

        hp.Hyperparameter_ID,
        hp.Type AS Hyperparameter_Type,
        hp.Epochs,
        hp.Value AS Hyperparameter_Value,

        mt.Metric_ID,
        mt.Name AS Metric_Name,
        mt.Value AS Metric_Value,
        mt.TimeStamp AS Metric_Timestamp

    FROM Experiment e
    LEFT JOIN User u ON e.Author_ID = u.User_ID
    LEFT JOIN Dataset d ON e.DataSet_ID = d.DataSet_ID
    LEFT JOIN Model m ON e.Model_ID = m.Model_ID
    LEFT JOIN Trial t ON e.Experiment_ID = t.Experiment_ID
    LEFT JOIN Hyperparameter hp ON t.Trial_ID = hp.Trial_ID
    LEFT JOIN Metric mt ON t.Trial_ID = mt.Trial_ID
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@task
def create_composite_key(df: pd.DataFrame) -> pd.DataFrame:
    df["Composite_ID"] = (
        df["Experiment_ID"].astype(str) + "_" +
        df["Trial_ID"].astype(str) + "_" +
        df["Model_ID"].astype(str) + "_" +
        df["DataSet_ID"].astype(str) + "_" +
        df["Metric_ID"].fillna("NULL").astype(str) + "_" +
        df["Hyperparameter_ID"].fillna("NULL").astype(str)
    )
    return df

@task
def count_unique_extracted_composite_keys(df: pd.DataFrame) -> int:
    unique_count = df["Composite_ID"].nunique()
    print(f"Unique Composite_IDs in Extracted Data: {unique_count}.")
    return unique_count

@task
def count_composite_keys_in_duckdb() -> int:
    conn = duckdb.connect(DUCKDB_PATH)

    # Check if table exists
    table_exists = conn.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_name = 'experiment_flat'
    """).fetchone()[0]

    if table_exists == 0:
        print("No data table found in DuckDB.")
        conn.close()
        return 0

    # Count unique Composite_IDs
    result = conn.execute("SELECT COUNT(DISTINCT Composite_ID) FROM experiment_flat").fetchone()[0]
    conn.close()
    print(f"Unique Composite_IDs in DuckDB: {result}")
    return result


@task
def load_to_duckdb(df: pd.DataFrame):
    conn = duckdb.connect(DUCKDB_PATH)

    # We choose to drop any existing data as this flow should be done once at the beginning
    #   of the MLED pipeline.
    conn.execute("DROP TABLE IF EXISTS experiment_flat")
    conn.execute("CREATE TABLE experiment_flat AS SELECT * FROM df")

    conn.close()
    print(f"Inserted {len(df)} rows into DuckDB table 'experiment_flat'.")

@task
def deduplicate_duckdb():
    conn = duckdb.connect(DUCKDB_PATH)

    conn.execute("""
        CREATE OR REPLACE TABLE experiment_flat AS
        SELECT * FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY Composite_ID ORDER BY Trial_ID) AS rn
            FROM experiment_flat
        )
        WHERE rn = 1
    """)
    
    # Drop rn after filtering
    conn.execute("""
        ALTER TABLE experiment_flat DROP COLUMN rn
    """)

    conn.close()
    print("Deduplication complete: only one row per Composite_ID retained.")

@task
def log_etl_run(
    extracted_count: int,
    pre_load_count: int,
    post_dedup_count: int,
    etl_type: str = "FULL",
    log_path: str = "etl_log.txt"
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = (
        f"{timestamp} | Type: {etl_type.upper()} | "
        f"Extracted: {extracted_count} | "
        f"Pre-Load: {pre_load_count} | "
        f"Post-Dedup: {post_dedup_count}\n"
    )

    with open(log_path, "a") as log_file:
        log_file.write(log_line)

    print(f"ETL summary logged as '{etl_type.upper()}' to text file.")

@flow
def ml_experiment_etl():
    #extract the full database
    extracted_data = extract_all_data()

    #create the unique composite keys
    extracted_data = create_composite_key(extracted_data)

    #count the unique extracted rows
    num_unique_extracted = count_unique_extracted_composite_keys(extracted_data)

    #count the unique number of rows in duckdb pre-load
    pre_load_count = count_composite_keys_in_duckdb()

    #load data into duckdb
    load_to_duckdb(extracted_data)

    #delete duplicate rows from duckdb
    deduplicate_duckdb()

    #count the unique number of rows in duckdb post-load
    post_load_count = count_composite_keys_in_duckdb()

    #log ETL run
    log_etl_run(num_unique_extracted, pre_load_count, post_load_count)

# Run the flow manually
if __name__ == "__main__":
    ml_experiment_etl()

