import sqlite3
from datetime import datetime
import uuid

def create_database2(database_name="test.db", conn=None):
    """Create SQLite database tables in the specified database."""
    is_test_db = conn is not None  # Track if we're using a test database
    
    if conn is None:
        conn = sqlite3.connect(database_name)  # Use persistent database
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # (Table creation scripts remain unchanged)

    conn.commit()

    if conn is None:
        conn = sqlite3.connect(database_name)
        should_close = True  # Only close if we created the connection
    else:
        should_close = False


    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS User (
        User_ID TEXT PRIMARY KEY,
        First_Name TEXT NOT NULL,
        Last_Name TEXT,
        Email TEXT UNIQUE NOT NULL,
        Role TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Dataset (
        DataSet_ID TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        Version INTEGER,
        Description TEXT NOT NULL,
        Storage_Location TEXT NOT NULL,
        Size INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Model (
        Model_ID TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT NOT NULL,
        Version INTEGER,
        Hyperparameters TEXT,
        ArtifactLocation TEXT
    );

    CREATE TABLE IF NOT EXISTS Experiment (
        Experiment_ID TEXT PRIMARY KEY,
        Name TEXT NOT NULL,
        Author_ID TEXT NOT NULL,
        Description TEXT NOT NULL,
        StartTimeStamp DATETIME NOT NULL,
        EndTimeStamp DATETIME NOT NULL,
        Status TEXT NOT NULL,
        Model_ID TEXT NOT NULL,
        DataSet_ID TEXT NOT NULL,
        FOREIGN KEY (Author_ID) REFERENCES User(User_ID),
        FOREIGN KEY (Model_ID) REFERENCES Model(Model_ID),
        FOREIGN KEY (DataSet_ID) REFERENCES Dataset(DataSet_ID)
    );

    CREATE TABLE IF NOT EXISTS Trial (
        Trial_ID TEXT PRIMARY KEY,
        Experiment_ID TEXT NOT NULL,
        Status TEXT NOT NULL,
        StartTime DATETIME NOT NULL,
        EndTime DATETIME NOT NULL,
        Seed INTEGER,
        FOREIGN KEY (Experiment_ID) REFERENCES Experiment(Experiment_ID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Metric (
        Metric_ID TEXT PRIMARY KEY,
        Trial_ID TEXT NOT NULL,
        Name TEXT NOT NULL,
        Value INTEGER NOT NULL,
        TimeStamp DATETIME NOT NULL,
        FOREIGN KEY (Trial_ID) REFERENCES Trial(Trial_ID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Hyperparameter (
        Hyperparameter_ID TEXT PRIMARY KEY,
        Trial_ID TEXT NOT NULL,
        Type TEXT,
        Epochs INTEGER,
        Value INTEGER NOT NULL,
        FOREIGN KEY (Trial_ID) REFERENCES Trial(Trial_ID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ErrorLog (
        Error_ID TEXT PRIMARY KEY,
        Experiment_ID TEXT NOT NULL,
        Trial_ID TEXT NOT NULL,
        TimeStamp DATETIME NOT NULL,
        ErrorMessage TEXT NOT NULL,
        ErrorDetails TEXT NOT NULL,
        FOREIGN KEY (Experiment_ID) REFERENCES Experiment(Experiment_ID) ON DELETE CASCADE,
        FOREIGN KEY (Trial_ID) REFERENCES Trial(Trial_ID) ON DELETE CASCADE
    );
    """)

    conn.commit()
    #if database_name != ":memory:":  # Only close if it's not an in-memory test
        #conn.close()

    if should_close:
        conn.close()
    print("Database and tables created successfully.")


if __name__ == '__main__':

    database = "test.db"

    create_database2(database)