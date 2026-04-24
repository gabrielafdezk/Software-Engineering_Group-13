import unittest
import os
from controllers.app_controller import AppController


class TestIntegration(unittest.TestCase):
    """
    Integration tests for the AppController and TaskModel working together.
    """

    def setUp(self):
        """
        Runs before each test.
        Creates a controller using a separate test CSV file.
        """
        self.test_file = "data/test_integration.csv"
        self.controller = AppController(self.test_file)

    def tearDown(self):
        """
        Runs after each test.
        Deletes the test CSV file.
        """
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_and_retrieve(self):
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        tasks = self.controller.get_all_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["name"], "Lab Report")

    def test_add_task_empty_name_returns_error(self):
        result = self.controller.add_task("", "25WSB301", "2026-12-01", "High")

        self.assertIn("error", result)

    def test_add_task_invalid_deadline_returns_error(self):
        result = self.controller.add_task("Lab Report", "25WSB301", "bad-date", "High")

        self.assertIn("error", result)

    def test_add_task_saves_to_csv(self):
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        self.assertTrue(os.path.exists(self.test_file))

    def test_add_then_delete_task(self):
        task = self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        result = self.controller.delete_task(task["id"])
        tasks = self.controller.get_all_tasks()

        self.assertTrue(result)
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent_task(self):
        result = self.controller.delete_task(999)

        self.assertFalse(result)

    def test_add_then_update_task(self):
        task = self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        result = self.controller.update_task(task["id"], status="Completed")
        tasks = self.controller.get_all_tasks()

        self.assertTrue(result)
        self.assertEqual(tasks[0]["status"], "Completed")

    def test_update_invalid_deadline_returns_error(self):
        task = self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        result = self.controller.update_task(task["id"], deadline="bad-date")

        self.assertIn("error", result)

    def test_filter_tasks_by_status(self):
        self.controller.add_task("Task 1", "25WSB301", "2026-12-01", "High", "Completed")
        self.controller.add_task("Task 2", "25WSB301", "2026-12-02", "Low", "Pending")

        result = self.controller.filter_tasks(status="Completed")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Task 1")

    def test_filter_tasks_by_search(self):
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        self.controller.add_task("Essay Plan", "25ENG201", "2026-12-02", "Low")

        result = self.controller.filter_tasks(search="lab")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Lab Report")

    def test_dashboard_summary_correct_counts(self):
        self.controller.add_task("Task 1", "25WSB301", "2026-12-01", "High", "Completed")
        self.controller.add_task("Task 2", "25WSB301", "2026-12-02", "Low", "Pending")

        summary = self.controller.get_dashboard_summary()

        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["pending"], 1)

    def test_dashboard_summary_next_deadline(self):
        self.controller.add_task("Task 1", "25WSB301", "2026-12-10", "High")
        self.controller.add_task("Task 2", "25WSB301", "2026-12-01", "Low")

        summary = self.controller.get_dashboard_summary()

        self.assertEqual(summary["next_deadline"]["name"], "Task 2")

    def test_dashboard_summary_empty(self):
        summary = self.controller.get_dashboard_summary()

        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["completed"], 0)
        self.assertEqual(summary["pending"], 0)
        self.assertIsNone(summary["next_deadline"])

    def test_get_all_tasks_includes_urgency(self):
        self.controller.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        tasks = self.controller.get_all_tasks()

        self.assertIn("urgency", tasks[0])

    def test_get_modules_returns_unique_list(self):
        self.controller.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.controller.add_task("Task 2", "25MAT102", "2026-12-02", "Low")
        self.controller.add_task("Task 3", "25WSB301", "2026-12-03", "Medium")

        modules = self.controller.get_modules()

        self.assertEqual(len(modules), 2)
        self.assertIn("25WSB301", modules)
        self.assertIn("25MAT102", modules)

    def test_get_tasks_for_calendar(self):
        self.controller.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.controller.add_task("Task 2", "25MAT102", "2026-12-01", "Low")

        calendar_data = self.controller.get_tasks_for_calendar()

        self.assertIn("2026-12-01", calendar_data)
        self.assertEqual(len(calendar_data["2026-12-01"]), 2)


if __name__ == "__main__":
    unittest.main()