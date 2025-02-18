import unittest
import sqlite3
from create_database2 import create_database2

class TestCreateDatabase(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory database for testing."""
        self.conn = sqlite3.connect(":memory:")  # Use shared in-memory DB
        self.conn.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign keys are enabled
        self.cursor = self.conn.cursor()
        create_database2(conn=self.conn)  # Pass connection to use in-memory DB

    def tearDown(self):
        """Ensure connection is not prematurely closed during tests."""
        if self.conn:
            self.conn.close()

    def test_tables_exist(self):
        """Check if all tables were created successfully."""
        expected_tables = {"User", "Dataset", "Model", "Experiment", "Trial", "Metric", "Hyperparameter", "ErrorLog"}
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row[0] for row in self.cursor.fetchall()}
        self.assertTrue(expected_tables.issubset(existing_tables), f"Missing tables: {expected_tables - existing_tables}")

    def test_user_table_schema(self):
        """Verify the schema of the User table."""
        try:
            self.cursor.execute("PRAGMA table_info(User);")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            expected_schema = {
                "User_ID": "TEXT",
                "First_Name": "TEXT",
                "Last_Name": "TEXT",
                "Email": "TEXT",
                "Role": "TEXT"
            }
            self.assertEqual(columns, expected_schema, "User table schema is incorrect.")
        except Exception as e:
            self.fail(f"Error testing User table schema: {e}")

    def test_dataset_table_schema(self):
        """Verify the schema of the Dataset table."""
        try:
            self.cursor.execute("PRAGMA table_info(Dataset);")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            expected_schema = {
                "DataSet_ID": "TEXT",
                "Name": "TEXT",
                "Version": "INTEGER",
                "Description": "TEXT",
                "Storage_Location": "TEXT",
                "Size": "INTEGER"
            }
            self.assertEqual(columns, expected_schema, "Dataset table schema is incorrect.")
        except Exception as e:
            self.fail(f"Error testing Dataset table schema: {e}")

    def test_model_table_schema(self):
        """Verify the schema of the Model table."""
        try:
            self.cursor.execute("PRAGMA table_info(Model);")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            expected_schema = {
                "Model_ID": "TEXT",
                "Name": "TEXT",
                "Type": "TEXT",
                "Version": "INTEGER",
                "Hyperparameters": "TEXT",
                "ArtifactLocation": "TEXT"
            }
            self.assertEqual(columns, expected_schema, "Model table schema is incorrect.")
        except Exception as e:
            self.fail(f"Error testing Model table schema: {e}")

    def test_experiment_table_foreign_keys(self):
        """Verify that the Experiment table has correct foreign keys."""
        try:
            self.cursor.execute("PRAGMA foreign_key_list(Experiment);")
            foreign_keys = {row[3]: row[2] for row in self.cursor.fetchall()}
            expected_fks = {
                "Author_ID": "User",
                "Model_ID": "Model",
                "DataSet_ID": "Dataset"
            }
            self.assertEqual(foreign_keys, expected_fks, "Experiment table foreign keys are incorrect.")
        except Exception as e:
            self.fail(f"Error testing Experiment table foreign keys: {e}")

    def test_trial_table_foreign_keys(self):
        """Verify that the Trial table has correct foreign keys."""
        try:
            self.cursor.execute("PRAGMA foreign_key_list(Trial);")
            foreign_keys = {row[3]: row[2] for row in self.cursor.fetchall()}
            expected_fks = {
                "Experiment_ID": "Experiment"
            }
            self.assertEqual(foreign_keys, expected_fks, "Trial table foreign keys are incorrect.")
        except Exception as e:
            self.fail(f"Error testing Trial table foreign keys: {e}")

    def test_metric_table_schema(self):
        """Verify the schema of the Metric table."""
        try:
            self.cursor.execute("PRAGMA table_info(Metric);")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            expected_schema = {
                "Metric_ID": "TEXT",
                "Trial_ID": "TEXT",
                "Name": "TEXT",
                "Value": "INTEGER",
                "TimeStamp": "DATETIME"
            }
            self.assertEqual(columns, expected_schema, "Metric table schema is incorrect.")
        except Exception as e:
            self.fail(f"Error testing Metric table schema: {e}")

    def test_hyperparameter_table_schema(self):
        """Verify the schema of the Hyperparameter table."""
        try:
            self.cursor.execute("PRAGMA table_info(Hyperparameter);")
            columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            expected_schema = {
                "Hyperparameter_ID": "TEXT",
                "Trial_ID": "TEXT",
                "Type": "TEXT",
                "Epochs": "INTEGER",
                "Value": "INTEGER"
            }
            self.assertEqual(columns, expected_schema, "Hyperparameter table schema is incorrect.")
        except Exception as e:
            self.fail(f"Error testing Hyperparameter table schema: {e}")

    def test_hyperparameter_table_foreign_keys(self):
        """Verify that the Hyperparameter table has correct foreign keys."""
        try:
            self.cursor.execute("PRAGMA foreign_key_list(Hyperparameter);")
            foreign_keys = {row[3]: row[2] for row in self.cursor.fetchall()}
            expected_fks = {
                "Trial_ID": "Trial"
            }
            self.assertEqual(foreign_keys, expected_fks, "Hyperparameter table foreign keys are incorrect.")
        except Exception as e:
            self.fail(f"Error testing Hyperparameter table foreign keys: {e}")

    def test_errorlog_table_foreign_keys(self):
        """Verify that the ErrorLog table has correct foreign keys."""
        try:
            self.cursor.execute("PRAGMA foreign_key_list(ErrorLog);")
            foreign_keys = {row[3]: row[2] for row in self.cursor.fetchall()}
            expected_fks = {
                "Experiment_ID": "Experiment",
                "Trial_ID": "Trial"
            }
            self.assertEqual(foreign_keys, expected_fks, "ErrorLog table foreign keys are incorrect.")
        except Exception as e:
            self.fail(f"Error testing ErrorLog table foreign keys: {e}")


    def test_experiment_table_foreign_keys(self):
        """Verify that the Experiment table has correct foreign keys."""
        self.cursor.execute("PRAGMA foreign_key_list(Experiment);")
        foreign_keys = {row[3]: row[2] for row in self.cursor.fetchall()}
        expected_fks = {
            "Author_ID": "User",
            "Model_ID": "Model",
            "DataSet_ID": "Dataset"
        }
        for column, ref_table in expected_fks.items():
            self.assertEqual(foreign_keys.get(column), ref_table, 
                             f"Foreign key {column} references wrong table.")

    def test_trial_table_foreign_keys(self):
        """Verify that the Trial table has correct foreign keys."""
        self.cursor.execute("PRAGMA foreign_key_list(Trial);")
        foreign_keys = {row[3]: row[2] for row in self.cursor.fetchall()}
        self.assertEqual(foreign_keys.get("Experiment_ID"), "Experiment", 
                         "Trial.Experiment_ID should reference Experiment.")

    def test_errorlog_table_foreign_keys(self):
        """Verify that the ErrorLog table has correct foreign keys."""
        self.cursor.execute("PRAGMA foreign_key_list(ErrorLog);")
        foreign_keys = {row[3]: row[2] for row in self.cursor.fetchall()}  # Only check reference table

        expected_fks = {
            "Experiment_ID": "Experiment",
            "Trial_ID": "Trial"
        }

        for column, ref_table in expected_fks.items():
            self.assertEqual(foreign_keys.get(column), ref_table, 
                            f"Foreign key {column} is incorrect.")
            
    def test_user_email_unique_constraint(self):
        """Ensure that inserting a duplicate email in User table raises an integrity error."""
        try:
            self.cursor.execute("INSERT INTO User (User_ID, First_Name, Last_Name, Email, Role) VALUES ('1', 'Alice', 'Smith', 'alice@example.com', 'Admin')")
            self.cursor.execute("INSERT INTO User (User_ID, First_Name, Last_Name, Email, Role) VALUES ('2', 'Bob', 'Jones', 'alice@example.com', 'User')")
            self.fail("Expected UNIQUE constraint failure on duplicate email, but test passed.")
        except sqlite3.IntegrityError:
            pass  # Test passes if IntegrityError is raised

    def test_dataset_name_unique_constraint(self):
        """Ensure that inserting a duplicate dataset name raises an integrity error."""
        try:
            self.cursor.execute("INSERT INTO Dataset (DataSet_ID, Name, Version, Description, Storage_Location, Size) VALUES ('1', 'Dataset1', 1, 'Test', 'local', 100)")
            self.cursor.execute("INSERT INTO Dataset (DataSet_ID, Name, Version, Description, Storage_Location, Size) VALUES ('2', 'Dataset1', 2, 'Test2', 'remote', 200)")
            self.fail("Expected UNIQUE constraint failure on duplicate dataset name, but test passed.")
        except sqlite3.IntegrityError:
            pass  # Test passes if IntegrityError is raised

    def test_experiment_delete_cascades_to_trials(self):
        """Ensure deleting an Experiment deletes all associated Trials due to ON DELETE CASCADE."""
        
        # Insert required parent records first
        self.cursor.execute("INSERT INTO User (User_ID, First_Name, Last_Name, Email, Role) VALUES ('1', 'John', 'Doe', 'john@example.com', 'Admin')")
        self.cursor.execute("INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES ('1', 'TestModel', 'CNN', 1, 'params', 'path')")
        self.cursor.execute("INSERT INTO Dataset (DataSet_ID, Name, Version, Description, Storage_Location, Size) VALUES ('1', 'TestDataset', 1, 'Desc', 'local', 100)")

        # Now insert Experiment and Trial
        self.cursor.execute("INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, EndTimeStamp, Status, Model_ID, DataSet_ID) VALUES ('1', 'Experiment1', '1', 'Test', '2024-01-01', '2024-01-02', 'Completed', '1', '1')")
        self.cursor.execute("INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, Seed) VALUES ('1', '1', 'Running', '2024-01-01', '2024-01-02', 123)")

        # Delete the parent record
        self.cursor.execute("DELETE FROM Experiment WHERE Experiment_ID = '1'")

        # Verify cascade delete
        self.cursor.execute("SELECT * FROM Trial WHERE Experiment_ID = '1'")
        result = self.cursor.fetchall()
        self.assertEqual(len(result), 0, "Cascade delete failed: Trials were not deleted when Experiment was removed.")


    def test_trial_delete_cascades_to_metrics(self):
        """Ensure deleting a Trial deletes all associated Metrics due to ON DELETE CASCADE."""
        
        # Insert required parent records first
        self.cursor.execute("INSERT INTO User (User_ID, First_Name, Last_Name, Email, Role) VALUES ('1', 'John', 'Doe', 'john@example.com', 'Admin')")
        self.cursor.execute("INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES ('1', 'TestModel', 'CNN', 1, 'params', 'path')")
        self.cursor.execute("INSERT INTO Dataset (DataSet_ID, Name, Version, Description, Storage_Location, Size) VALUES ('1', 'TestDataset', 1, 'Desc', 'local', 100)")
        self.cursor.execute("INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, EndTimeStamp, Status, Model_ID, DataSet_ID) VALUES ('1', 'Experiment1', '1', 'Test', '2024-01-01', '2024-01-02', 'Completed', '1', '1')")

        # Now insert Trial and Metric
        self.cursor.execute("INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, Seed) VALUES ('1', '1', 'Running', '2024-01-01', '2024-01-02', 123)")
        self.cursor.execute("INSERT INTO Metric (Metric_ID, Trial_ID, Name, Value, TimeStamp) VALUES ('1', '1', 'Accuracy', 95.0, '2024-01-02')")

        # Delete the parent record
        self.cursor.execute("DELETE FROM Trial WHERE Trial_ID = '1'")

        # Verify cascade delete
        self.cursor.execute("SELECT * FROM Metric WHERE Trial_ID = '1'")
        result = self.cursor.fetchall()
        self.assertEqual(len(result), 0, "Cascade delete failed: Metrics were not deleted when Trial was removed.")


if __name__ == "__main__":
    unittest.main()
