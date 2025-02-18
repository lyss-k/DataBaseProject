import sqlite3
from datetime import datetime
import uuid

def create_database(conn=None):
    if conn is None:
        conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create User Table
    cursor.execute("""
    CREATE TABLE User (
        User_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        First_Name TEXT NOT NULL,
        Last_Name TEXT,
        Email TEXT UNIQUE NOT NULL,
        Role TEXT NOT NULL
    );
    """)

    # Create Dataset Table
    cursor.execute("""
    CREATE TABLE Dataset (
        DataSet_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        Name TEXT UNIQUE NOT NULL,
        Version INTEGER,
        Description TEXT NOT NULL,
        Storage_Location TEXT NOT NULL,
        Size INTEGER NOT NULL
    );
    """)

    # Create Model Table
    cursor.execute("""
    CREATE TABLE Model (
        Model_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        Name TEXT UNIQUE NOT NULL,
        Type TEXT NOT NULL, -- (Neural Net, Decision Tree, Regression, etc.)
        Version INTEGER,
        Hyperparameters TEXT,
        ArtifactLocation TEXT
    );
    """)

    # Create Experiment Table
    cursor.execute("""
    CREATE TABLE Experiment (
        Experiment_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        Name TEXT UNIQUE NOT NULL,
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
    """)

    # Create Hyperparameter Table
    cursor.execute("""
    CREATE TABLE Hyperparameter (
        Hyperparameter_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        Trial_ID TEXT NOT NULL,
        Type TEXT,  -- (Learning Rate, Batch Size, etc.)
        Epochs INTEGER,
        Value INTEGER NOT NULL,
        FOREIGN KEY (Trial_ID) REFERENCES Trial(Trial_ID) ON DELETE CASCADE
    );
    """)

    # Create Metric Table
    cursor.execute("""
    CREATE TABLE Metric (
        Metric_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        Trial_ID TEXT NOT NULL,
        Name TEXT NOT NULL,
        Value INTEGER NOT NULL,
        TimeStamp DATETIME NOT NULL,
        FOREIGN KEY (Trial_ID) REFERENCES Trial(Trial_ID) ON DELETE CASCADE
    );
    """)

    # Create ErrorLog Table
    cursor.execute("""
    CREATE TABLE ErrorLog (
        Error_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        Experiment_ID TEXT NOT NULL,
        Trial_ID TEXT NOT NULL,
        TimeStamp DATETIME NOT NULL,
        ErrorMessage TEXT NOT NULL,
        ErrorDetails TEXT NOT NULL,
        FOREIGN KEY (Experiment_ID) REFERENCES Experiment(Experiment_ID) ON DELETE CASCADE,
        FOREIGN KEY (Trial_ID) REFERENCES Trial(Trial_ID) ON DELETE CASCADE
    );
    """)

    # Create Trial Table
    cursor.execute("""
    CREATE TABLE Trial (
        Trial_ID TEXT PRIMARY KEY DEFAULT (uuid()),
        Experiment_ID TEXT NOT NULL,
        Status TEXT NOT NULL,
        StartTime DATETIME NOT NULL,
        EndTime DATETIME NOT NULL,
        Seed INTEGER,
        FOREIGN KEY (Experiment_ID) REFERENCES Experiment(Experiment_ID) ON DELETE CASCADE
    );
    """)

    # Commit and close connection
    conn.commit()
    conn.close()

    print("Database and tables created successfully.")


if __name__ == '__main__':

    database = "test.db"

    create_database(database)