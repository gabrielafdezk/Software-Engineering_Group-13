import unittest
import os
import csv
from models.task_model import TaskModel

class TestTaskModel(unittest.TestCase):
    """
    Unit tests for the TaskModel class.
    Each test checks one specific method works correctly.
    """

    def setUp(self):
        """
        Runs before every single test.
        Creates a fresh TaskModel with a temporary test CSV file
        so tests don't interfere with each other or real data.
        """
        self.test_file = "data/test_tasks.csv"
        self.model = TaskModel()
        self.model.DATA_FILE = self.test_file
        self.model.tasks = []
        self.model.next_id = 1

    def tearDown(self):
        """
        Runs after every single test.
        Deletes the temporary test CSV file to keep things clean.
        """
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    # -------------------------
    # ADD TASK TESTS
    # -------------------------

    def test_add_task_successfully(self):
        """Test that a valid task is added correctly."""
        task = self.model.add_task(
            name="Lab Report",
            module="25WSB301",
            deadline="2026-12-01",
            priority="High"
        )
        self.assertEqual(task["name"], "Lab Report")
        self.assertEqual(task["module"], "25WSB301")
        self.assertEqual(task["priority"], "High")
        self.assertEqual(task["status"], "Pending")
        self.assertEqual(len(self.model.tasks), 1)

    def test_add_task_empty_name_raises_error(self):
        """Test that adding a task with an empty name raises a ValueError."""
        with self.assertRaises(ValueError):
            self.model.add_task(
                name="",
                module="25WSB301",
                deadline="2026-12-01",
                priority="High"
            )

    def test_add_task_whitespace_name_raises_error(self):
        """Test that a name with only spaces is also rejected."""
        with self.assertRaises(ValueError):
            self.model.add_task(
                name="   ",
                module="25WSB301",
                deadline="2026-12-01",
                priority="High"
            )

    def test_add_multiple_tasks_increments_id(self):
        """Test that each new task gets a unique incrementing id."""
        task1 = self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        task2 = self.model.add_task("Task 2", "25WSB301", "2026-12-02", "Low")
        self.assertEqual(task1["id"], 1)
        self.assertEqual(task2["id"], 2)

    # -------------------------
    # DELETE TASK TESTS
    # -------------------------

    def test_delete_task_successfully(self):
        """Test that a task is removed correctly by id."""
        task = self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        result = self.model.delete_task(task["id"])
        self.assertTrue(result)
        self.assertEqual(len(self.model.tasks), 0)

    def test_delete_task_wrong_id_returns_false(self):
        """Test that deleting a non-existent id returns False."""
        result = self.model.delete_task(999)
        self.assertFalse(result)

    # -------------------------
    # UPDATE TASK TESTS
    # -------------------------

    def test_update_task_status(self):
        """Test that a task's status can be updated correctly."""
        task = self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        result = self.model.update_task(task["id"], status="Completed")
        self.assertTrue(result)
        self.assertEqual(self.model.tasks[0]["status"], "Completed")

    def test_update_task_multiple_fields(self):
        """Test that multiple fields can be updated at once."""
        task = self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        self.model.update_task(task["id"], priority="Low", status="Completed")
        self.assertEqual(self.model.tasks[0]["priority"], "Low")
        self.assertEqual(self.model.tasks[0]["status"], "Completed")

    def test_update_task_wrong_id_returns_false(self):
        """Test that updating a non-existent task returns False."""
        result = self.model.update_task(999, status="Completed")
        self.assertFalse(result)

    # -------------------------
    # GET ALL TESTS
    # -------------------------

    def test_get_all_returns_all_tasks(self):
        """Test that get_all returns every task."""
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Task 2", "25MAT102", "2026-12-02", "Low")
        tasks = self.model.get_all()
        self.assertEqual(len(tasks), 2)

    def test_get_all_empty_returns_empty_list(self):
        """Test that get_all returns an empty list when there are no tasks."""
        tasks = self.model.get_all()
        self.assertEqual(tasks, [])

    # -------------------------
    # FILTER TESTS
    # -------------------------

    def test_filter_by_status(self):
        """Test filtering tasks by status."""
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High", "Completed")
        self.model.add_task("Task 2", "25WSB301", "2026-12-02", "Low", "Pending")
        result = self.model.filter_by(status="Completed")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Task 1")

    def test_filter_by_priority(self):
        """Test filtering tasks by priority."""
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Task 2", "25WSB301", "2026-12-02", "Low")
        result = self.model.filter_by(priority="High")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Task 1")

    def test_filter_by_module(self):
        """Test filtering tasks by module code."""
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Task 2", "25MAT102", "2026-12-02", "Low")
        result = self.model.filter_by(module="25WSB301")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["module"], "25WSB301")

    def test_filter_by_search(self):
        """Test searching tasks by name."""
        self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Essay Plan", "25ENG201", "2026-12-02", "Low")
        result = self.model.filter_by(search="lab")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Lab Report")

    # -------------------------
    # URGENCY TESTS
    # -------------------------

    def test_urgency_red(self):
        """Test that a deadline today or tomorrow returns red."""
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        self.assertEqual(self.model.get_urgency(tomorrow), "red")

    def test_urgency_amber(self):
        """Test that a deadline within 7 days returns amber."""
        from datetime import date, timedelta
        in_5_days = (date.today() + timedelta(days=5)).isoformat()
        self.assertEqual(self.model.get_urgency(in_5_days), "amber")

    def test_urgency_green(self):
        """Test that a deadline more than 7 days away returns green."""
        from datetime import date, timedelta
        in_30_days = (date.today() + timedelta(days=30)).isoformat()
        self.assertEqual(self.model.get_urgency(in_30_days), "green")

    def test_urgency_invalid_date(self):
        """Test that an invalid date defaults to green."""
        self.assertEqual(self.model.get_urgency("not-a-date"), "green")

    # -------------------------
    # SAVE AND LOAD TESTS
    # -------------------------

    def test_save_and_load(self):
        """Test that tasks are saved to CSV and loaded back correctly."""
        self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        
        # Create a new model instance pointing to the same test file
        new_model = TaskModel()
        new_model.DATA_FILE = self.test_file
        new_model.tasks = []
        new_model.next_id = 1
        new_model.load()

        self.assertEqual(len(new_model.tasks), 1)
        self.assertEqual(new_model.tasks[0]["name"], "Lab Report")


if __name__ == "__main__":
    unittest.main()