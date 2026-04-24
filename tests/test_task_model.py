import unittest
import os
from datetime import date, timedelta
from models.task_model import TaskModel


class TestTaskModel(unittest.TestCase):
    """
    Unit tests for the TaskModel class.
    """

    def setUp(self):
        """
        Runs before each test.
        Uses a separate test CSV file.
        """
        self.test_file = "data/test_tasks.csv"
        self.model = TaskModel(self.test_file)

    def tearDown(self):
        """
        Runs after each test.
        Deletes the test CSV file.
        """
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_task_successfully(self):
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
        with self.assertRaises(ValueError):
            self.model.add_task(
                name="",
                module="25WSB301",
                deadline="2026-12-01",
                priority="High"
            )

    def test_add_task_whitespace_name_raises_error(self):
        with self.assertRaises(ValueError):
            self.model.add_task(
                name="   ",
                module="25WSB301",
                deadline="2026-12-01",
                priority="High"
            )

    def test_add_task_empty_module_raises_error(self):
        with self.assertRaises(ValueError):
            self.model.add_task(
                name="Lab Report",
                module="",
                deadline="2026-12-01",
                priority="High"
            )

    def test_add_task_invalid_deadline_raises_error(self):
        with self.assertRaises(ValueError):
            self.model.add_task(
                name="Lab Report",
                module="25WSB301",
                deadline="01-12-2026",
                priority="High"
            )

    def test_add_multiple_tasks_increments_id(self):
        task1 = self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        task2 = self.model.add_task("Task 2", "25WSB301", "2026-12-02", "Low")

        self.assertEqual(task1["id"], 1)
        self.assertEqual(task2["id"], 2)

    def test_delete_task_successfully(self):
        task = self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        result = self.model.delete_task(task["id"])

        self.assertTrue(result)
        self.assertEqual(len(self.model.tasks), 0)

    def test_delete_task_wrong_id_returns_false(self):
        result = self.model.delete_task(999)

        self.assertFalse(result)

    def test_update_task_status(self):
        task = self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        result = self.model.update_task(task["id"], status="Completed")

        self.assertTrue(result)
        self.assertEqual(self.model.tasks[0]["status"], "Completed")

    def test_update_task_multiple_fields(self):
        task = self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        self.model.update_task(task["id"], priority="Low", status="Completed")

        self.assertEqual(self.model.tasks[0]["priority"], "Low")
        self.assertEqual(self.model.tasks[0]["status"], "Completed")

    def test_update_task_invalid_deadline_raises_error(self):
        task = self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        with self.assertRaises(ValueError):
            self.model.update_task(task["id"], deadline="bad-date")

    def test_update_task_wrong_id_returns_false(self):
        result = self.model.update_task(999, status="Completed")

        self.assertFalse(result)

    def test_get_all_returns_all_tasks(self):
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Task 2", "25MAT102", "2026-12-02", "Low")

        tasks = self.model.get_all()

        self.assertEqual(len(tasks), 2)

    def test_get_all_empty_returns_empty_list(self):
        tasks = self.model.get_all()

        self.assertEqual(tasks, [])

    def test_filter_by_status(self):
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High", "Completed")
        self.model.add_task("Task 2", "25WSB301", "2026-12-02", "Low", "Pending")

        result = self.model.filter_by(status="Completed")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Task 1")

    def test_filter_by_priority(self):
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Task 2", "25WSB301", "2026-12-02", "Low")

        result = self.model.filter_by(priority="High")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Task 1")

    def test_filter_by_module(self):
        self.model.add_task("Task 1", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Task 2", "25MAT102", "2026-12-02", "Low")

        result = self.model.filter_by(module="25WSB301")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["module"], "25WSB301")

    def test_filter_by_search(self):
        self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")
        self.model.add_task("Essay Plan", "25ENG201", "2026-12-02", "Low")

        result = self.model.filter_by(search="lab")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Lab Report")

    def test_urgency_red(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        self.assertEqual(self.model.get_urgency(tomorrow), "red")

    def test_urgency_amber(self):
        in_5_days = (date.today() + timedelta(days=5)).isoformat()

        self.assertEqual(self.model.get_urgency(in_5_days), "amber")

    def test_urgency_green(self):
        in_30_days = (date.today() + timedelta(days=30)).isoformat()

        self.assertEqual(self.model.get_urgency(in_30_days), "green")

    def test_urgency_invalid_date(self):
        self.assertEqual(self.model.get_urgency("not-a-date"), "green")

    def test_save_and_load(self):
        self.model.add_task("Lab Report", "25WSB301", "2026-12-01", "High")

        new_model = TaskModel(self.test_file)

        self.assertEqual(len(new_model.tasks), 1)
        self.assertEqual(new_model.tasks[0]["name"], "Lab Report")


if __name__ == "__main__":
    unittest.main()