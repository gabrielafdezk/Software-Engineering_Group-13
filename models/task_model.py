import csv
import os
from datetime import date


class TaskModel:
    """
    Handles all data logic for the Smart-Task application.
    Responsible for storing, retrieving, and saving tasks.
    No UI code belongs here.
    """

    FIELDS = ["id", "name", "module", "deadline", "priority", "status"]

    def __init__(self, data_file="data/tasks.csv"):
        """
        Creates an empty task list and loads any saved tasks from the CSV file.
        """
        self.DATA_FILE = data_file
        self.tasks = []
        self.next_id = 1
        self.load()

    def load(self):
        """
        Loads tasks from the CSV file into memory.
        """
        if not os.path.exists(self.DATA_FILE):
            return

        with open(self.DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                row["id"] = int(row["id"])
                self.tasks.append(row)

            if self.tasks:
                self.next_id = max(t["id"] for t in self.tasks) + 1

    def save(self):
        """
        Saves all tasks to the CSV file.
        """
        folder = os.path.dirname(self.DATA_FILE)

        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(self.DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()
            writer.writerows(self.tasks)

    def add_task(self, name, module, deadline, priority, status="Pending"):
        """
        Creates a new task and saves it.
        """

        if not name or not name.strip():
            raise ValueError("Task name cannot be empty.")

        if not module or not module.strip():
            raise ValueError("Module cannot be empty.")

        try:
            date.fromisoformat(deadline)
        except ValueError:
            raise ValueError("Deadline must be in YYYY-MM-DD format.")

        task = {
            "id": self.next_id,
            "name": name.strip(),
            "module": module.strip(),
            "deadline": deadline,
            "priority": priority,
            "status": status
        }

        self.tasks.append(task)
        self.next_id += 1
        self.save()

        return task

    def delete_task(self, task_id):
        """
        Deletes a task using its id.
        """
        original_count = len(self.tasks)

        self.tasks = [
            task for task in self.tasks
            if task["id"] != task_id
        ]

        if len(self.tasks) < original_count:
            self.save()
            return True

        return False

    def update_task(self, task_id, **kwargs):
        """
        Updates one or more fields of an existing task.
        """

        for task in self.tasks:
            if task["id"] == task_id:
                for key, value in kwargs.items():
                    if key in self.FIELDS:
                        task[key] = value

                if not task["name"].strip():
                    raise ValueError("Task name cannot be empty.")

                if not task["module"].strip():
                    raise ValueError("Module cannot be empty.")

                try:
                    date.fromisoformat(task["deadline"])
                except ValueError:
                    raise ValueError("Deadline must be in YYYY-MM-DD format.")

                self.save()
                return True

        return False

    def get_all(self):
        """
        Returns a copy of all tasks.
        """
        return list(self.tasks)

    def filter_by(self, status=None, priority=None, module=None, search=None):
        """
        Filters tasks by status, priority, module, or search text.
        """
        results = self.tasks

        if status:
            results = [
                task for task in results
                if task["status"].lower() == status.lower()
            ]

        if priority:
            results = [
                task for task in results
                if task["priority"].lower() == priority.lower()
            ]

        if module:
            results = [
                task for task in results
                if task["module"].lower() == module.lower()
            ]

        if search:
            results = [
                task for task in results
                if search.lower() in task["name"].lower()
                or search.lower() in task["module"].lower()
            ]

        return list(results)

    def get_urgency(self, deadline_str):
        """
        Returns red, amber, or green depending on how close the deadline is.
        """
        try:
            deadline = date.fromisoformat(deadline_str)
            days_left = (deadline - date.today()).days

            if days_left <= 1:
                return "red"
            elif days_left <= 7:
                return "amber"
            else:
                return "green"

        except ValueError:
            return "green"