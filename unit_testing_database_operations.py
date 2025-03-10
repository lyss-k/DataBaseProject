import unittest
from database_operations import *
import time

class TestDatabaseOperations(unittest.TestCase):
    
    def test_insert_user_missing_fields(self):
        """Test inserting a user with missing required fields."""
        with self.assertLogs(level='ERROR') as log:
            insert_user("", "Doe", "", "Admin")
        self.assertIn("Error: First name, email, and role are required.", log.output[-1])

    def test_insert_dataset_invalid_size(self):
        """Test inserting a dataset with an invalid size."""
        with self.assertLogs(level='ERROR') as log:
            insert_dataset("Dataset1", 1, "Description", "Storage/Path", -10)
        self.assertIn("Error: Name, description, storage location, and a valid size are required.", log.output[-1])
    
    def test_insert_model_missing_fields(self):
        """Test inserting a model with missing required fields."""
        with self.assertLogs(level='ERROR') as log:
            insert_model("", "", 1, "Hyperparams", "Location")
        self.assertIn("Error: Name, model type, and artifact location are required.", log.output[-1])
    
    def test_insert_experiment_missing_fields(self):
        """Test inserting an experiment with missing required fields."""
        with self.assertLogs(level='ERROR') as log:
            insert_experiment("", "", "", "", "", "")
        self.assertIn("Error: All fields are required for inserting an experiment.", log.output[-1])
    
    def test_insert_trial_missing_fields(self):
        """Test inserting a trial with missing required fields."""
        with self.assertLogs(level='ERROR') as log:
            insert_trial("", "", "", "", None)
        self.assertIn("Error: Experiment ID, status, start time, and end time are required.", log.output[-1])
    
    def test_insert_metric_missing_fields(self):
        """Test inserting a metric with missing required fields."""
        with self.assertLogs(level='ERROR') as log:
            insert_metric("", "", None, "")
        self.assertIn("Error: Trial ID, name, value, and timestamp are required.", log.output[-1])
    
    def test_insert_hyperparameter_missing_fields(self):
        """Test inserting a hyperparameter with missing required fields."""
        with self.assertLogs(level='ERROR') as log:
            insert_hyperparameter("", "", None, None)
        self.assertIn("Error: Trial ID, type, and value are required.", log.output[-1])
    
    def test_insert_error_log_missing_fields(self):
        """Test inserting an error log with missing required fields."""
        with self.assertLogs(level='ERROR') as log:
            insert_error_log("", "", "", "", "")
        self.assertIn("Error: Experiment ID, trial ID, timestamp, error message, and error details are required.", log.output[-1])
    
    def test_delete_non_existent_record(self):
        """Test deleting a non-existent record and ensure correct error is logged."""
        with self.assertLogs(level='ERROR') as log:
            delete_row("User", "User_ID", "non-existent-id")

        expected_message = "Delete failed: No record found in User where User_ID = non-existent-id"
        self.assertTrue(any(expected_message in message for message in log.output), 
                        f"Expected log message not found: {log.output}")
    
    def test_update_non_existent_record(self):
        """Test updating a non-existent record."""
        with self.assertLogs(level='ERROR') as log:
            update_value("User", "Last_Name", "Knuckle", "Last_Name", "non-existent-id")
        expected_message = "Update failed: No record found in User where Last_Name = non-existent-id"
        self.assertTrue(any(expected_message in message for message in log.output), 
                    f"Expected log message not found: {log.output}")
        
    def test_update_existing_record(self):
        """Test updating an existing record successfully."""
        insert_user("Alice", "UpdateTest", "alice_update@example.com", "User")
        update_value("User", "First_Name", "UpdatedAlice", "Email", "alice_update@example.com")
        result = fetch_data("SELECT First_Name FROM User WHERE Email = ?", ("alice_update@example.com",))
        self.assertEqual(result[0][0], "UpdatedAlice")

    def test_insert_user_success(self):
        """Test inserting a user with valid inputs."""
        insert_user("John", "Doe", "johndoe@example.com", "Admin")
        result = fetch_data("SELECT * FROM User WHERE Email = ?", ("johndoe@example.com",))
        self.assertTrue(len(result) > 0)

    def test_integrity_error_on_duplicate_user(self):
        """Test inserting a duplicate user logs an integrity error."""
        insert_user("Bob", "Smith", "duplicate@example.com", "User")
        with self.assertLogs(level='ERROR') as log:
            insert_user("Bob", "Smith", "duplicate@example.com", "User")
        self.assertTrue(any("Integrity error:" in message for message in log.output))
    
    def test_insert_dataset_success(self):
        """Test inserting a dataset with valid inputs."""
        insert_dataset("Dataset1", 1, "Description", "Storage/Path", 100)
        result = fetch_data("SELECT * FROM Dataset WHERE Name = ?", ("Dataset1",))
        self.assertTrue(len(result) > 0)
    
    def test_insert_model_success(self):
        """Test inserting a model with valid inputs."""
        insert_model("Model1", "Neural Network", 1, "{hyperparams}", "Model/Path")
        result = fetch_data("SELECT * FROM Model WHERE Name = ?", ("Model1",))
        self.assertTrue(len(result) > 0)

    def test_insert_trial_success(self):
        """Test inserting a trial with valid inputs."""
        insert_trial("experiment-uuid", "Completed", "2024-02-12 12:00:00", "2024-02-12 14:00:00", 42)
        result = fetch_data("SELECT * FROM Trial WHERE Experiment_ID = ?", ("experiment-uuid",))
        self.assertTrue(len(result) > 0)

    def test_insert_metric_success(self):
        """Test inserting a metric with valid inputs."""
        insert_metric("trial-uuid", "Accuracy", 0.95, "2024-02-12 15:00:00")
        result = fetch_data("SELECT * FROM Metric WHERE Trial_ID = ?", ("trial-uuid",))
        self.assertTrue(len(result) > 0)

    def test_insert_hyperparameter_success(self):
        """Test inserting a hyperparameter with valid inputs."""
        insert_hyperparameter("trial-uuid", "Learning Rate", 50, 0.001)
        result = fetch_data("SELECT * FROM Hyperparameter WHERE Trial_ID = ?", ("trial-uuid",))
        self.assertTrue(len(result) > 0)

    def test_insert_error_log_success(self):
        """Test inserting an error log with valid inputs."""
        insert_error_log("experiment-uuid", "trial-uuid", "2024-02-12 16:00:00", "MemoryError", "Out of memory during training.")
        result = fetch_data("SELECT * FROM ErrorLog WHERE Trial_ID = ?", ("trial-uuid",))
        self.assertTrue(len(result) > 0)

    def test_fetch_data(self):
        """Test fetching data from an existing table."""
        result = fetch_data("SELECT name FROM sqlite_master WHERE type='table'")
        self.assertIsInstance(result, list)

    def test_delete_table_existing(self):
        """Test deleting an existing table."""
        execute_query("CREATE TABLE IF NOT EXISTS TempTable (id INTEGER PRIMARY KEY)")
        delete_table("TempTable")
        result = fetch_data("SELECT name FROM sqlite_master WHERE type='table' AND name='TempTable'", ())
        self.assertEqual(len(result), 0)

    def test_fetch_table(self):
        """Test fetching all rows from a table."""
        result = fetch_table("User")
        self.assertIsInstance(result, list)
    
    def test_delete_row(self):
        """Test deleting a specific row."""
        insert_user("Delete", "Me", "deleteme@example.com", "User")
        delete_row("User", "Email", "deleteme@example.com")
        result = fetch_data("SELECT * FROM User WHERE Email = ?", ("deleteme@example.com"))
        self.assertEqual(len(result), 0)
    
    def test_delete_table(self):
        """Test deleting an entire table."""
        delete_table("TestTable")
        result = fetch_data("SELECT name FROM sqlite_master WHERE type='table' AND name='TestTable'", ())
        self.assertEqual(len(result), 0)
    
    def test_fetch_experiments_by_author(self):
        """Test fetching experiments by author ID."""
        result = fetch_experiments_by_author("some-author-id")
        self.assertIsInstance(result, list)
    
    def test_count_records(self):
        """Test counting records in a table."""
        result = count_records("User")
        self.assertIsInstance(result, int)
    
    def test_get_latest_experiment(self):
        """Test retrieving the latest experiment."""
        result = get_latest_experiment()
        self.assertIsInstance(result, list)
    
    def test_get_active_experiments(self):
        """Test retrieving active experiments."""
        result = get_active_experiments()
        self.assertIsInstance(result, list)

    import time

#not sure if below here works
def test_bulk_insert_performance(self):
    """Test the performance of bulk user inserts."""
    users = [("User" + str(i), "Test", f"user{i}@test.com", "Member") for i in range(1000)]
    
    start_time = time.time()
    for user in users:
        insert_user(*user)
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f"Bulk insert of 1000 users took {execution_time:.2f} seconds.")
    
    self.assertLess(execution_time, 5)  # Ensure bulk insert completes within 5 seconds

def test_bulk_query_performance(self):
    """Test the performance of querying a large user dataset."""
    start_time = time.time()
    result = fetch_data("SELECT * FROM User")
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Fetching all users took {execution_time:.2f} seconds.")

    self.assertLess(execution_time, 3)  # Ensure query completes within 3 seconds

if __name__ == '__main__':
    unittest.main()
