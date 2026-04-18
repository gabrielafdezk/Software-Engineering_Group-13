import unittest
import os
from controllers.app_controller import AppController

class TestIntegration(unittest.TestCase):
    """
    Integration tests for the AppController and TaskModel working together.
    These tests check that the full flow works end-to-end — from the
    Controller calling the Model, all the way to data being saved and loaded.
    """

    def setUp(self):
        """
        Runs before every test.
        Creates a fresh AppController with a temporary test CSV file.
        """
        self.controller = AppController()
        self.test_file = "data/test_integration.csv"
        self.controller.model.DATA_FILE = self.test_file
        self.controller.model.tasks = []
        self.controller.model.next_id = 1

    def tearDown(self):
        """
        Runs after every test.
        Deletes the temporary test CSV file to keep things clean.
        """
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    # -------------------------
    # ADD TASK FLOW
    # -------------------------

    def test_add_task_and_retrieve(self):
        """Test that adding a task through the controller can be retrieved."""
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        tasks = self.controller.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["name"], "Lab Report")

    def test_add_task_empty_name_returns_error(self):
        """Test that adding a task with empty name returns an error dict."""
        result = self.controller.add_task("", "25WSB301", "2026-12-01", "High")
        self.assertIn("error", result)

    def test_add_task_saves_to_csv(self):
        """Test that adding a task through the controller saves it to CSV."""
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        self.assertTrue(os.path.exists(self.test_file))

    # -------------------------
    # DELETE TASK FLOW
    # -------------------------

    def test_add_then_delete_task(self):
        """Test that a task added through the controller can be deleted."""
        task = self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        result = self.controller.delete_task(task["id"])
        self.assertTrue(result)
        tasks = self.controller.get_all_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent_task(self):
        """Test that deleting a task that doesn't exist returns False."""
        result = self.controller.delete_task(999)
        self.assertFalse(result)

    # -------------------------
    # UPDATE TASK FLOW
    # -------------------------

    def test_add_then_update_task(self):
        """Test that a task can be updated through the controller."""
        task = self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        result = self.controller.update_task(task["id"], status="Completed")
        self.assertTrue(result)
        tasks = self.controller.get_all_tasks()
        self.assertEqual(tasks[0]["status"], "Completed")

    # -------------------------
    # FILTER TASK FLOW
    # -------------------------

    def test_filter_tasks_by_status(self):
        """Test that filtering by status works through the controller."""
        self.controller.add_task("Task 1", "25WSB301", "2026-12-01", "High", "Completed")
        self.controller.add_task("Task 2", "25WSB301", "2026-12-02", "Low", "Pending")
        result = self.controller.filter_tasks(status="Completed")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Task 1")

    def test_filter_tasks_by_search(self):
        """Test that searching by name works through the controller."""
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        self.controller.add_task("Essay Plan", "25ENG201", "2026-12-02", "Low")
        result = self.controller.filter_tasks(search="lab")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Lab Report")

    # -------------------------
    # DASHBOARD SUMMARY FLOW
    # -------------------------

    def test_dashboard_summary_correct_counts(self):
        """Test that the dashboard summary returns correct totals."""
        self.controller.add_task("Task 1", "25WSB301", "2026-12-01", "High", "Completed")
        self.controller.add_task("Task 2", "25WSB301", "2026-12-02", "Low", "Pending")
        summary = self.controller.get_dashboard_summary()
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["completed"], 1)

    def test_dashboard_summary_next_deadline(self):
        """Test that the dashboard returns the most urgent pending task."""
        self.controller.add_task("Task 1", "25WSB301", "2026-12-10", "High")
        self.controller.add_task("Task 2", "25WSB301", "2026-12-01", "Low")
        summary = self.controller.get_dashboard_summary()
        self.assertEqual(summary["next_deadline"]["name"], "Task 2")

    def test_dashboard_summary_empty(self):
        """Test dashboard summary when there are no tasks."""
        summary = self.controller.get_dashboard_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["completed"], 0)
        self.assertIsNone(summary["next_deadline"])

    # -------------------------
    # URGENCY FLOW
    # -------------------------

    def test_get_all_tasks_includes_urgency(self):
        """Test that get_all_tasks adds urgency colour to every task."""
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        tasks = self.controller.get_all_tasks()
        self.assertIn("urgency", tasks[0])

    # -------------------------
    # MODULES FLOW
    # -------------------------

    def test_get_modules_returns_unique_list(self):
        """Test that get_modules returns a sorted unique list of module codes."""
        self.controller.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.controller.add_task("Task 2", "25MAT102", "2026-12-02", "Low")
        self.controller.add_task("Task 3", "25WSB301", "2026-12-03", "Medium")
        modules = self.controller.get_modules()
        self.assertEqual(len(modules), 2)
        self.assertIn("25WSB301", modules)
        self.assertIn("25MAT102", modules)


if __name__ == "__main__":
    unittest.main()