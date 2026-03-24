import csv
import os
from datetime import date

class TaskModel:
    """
    Handles all data logic for the Smart-Task application.
    Responsible for storing, retrieving, and persisting tasks.
    No UI code belongs here.
    """

    # This is the file where tasks will be saved
    DATA_FILE = "data/tasks.csv"

    # These are the column names for the CSV file
    FIELDS = ["id", "name", "module", "deadline", "priority", "status"]

    def __init__(self):
        """
        Constructor — runs automatically when TaskModel() is called.
        Creates an empty task list and loads any saved tasks from the CSV.
        """
        self.tasks = []       # This is the list that holds all tasks in memory
        self.next_id = 1      # Each task gets a unique number so we can find it later
        self.load()           # Load saved tasks from the CSV file straight away

    def load(self):
        """
        Loads tasks from the CSV file into memory.
        If the file doesn't exist yet, it does nothing (first run).
        """
        # If the file doesn't exist yet, there's nothing to load
        if not os.path.exists(self.DATA_FILE):
            return

        with open(self.DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)  # Reads each row as a dictionary
            for row in reader:
                # Convert the id from text back to a number
                row["id"] = int(row["id"])
                self.tasks.append(row)

            # Set next_id to be one higher than the highest existing id
            if self.tasks:
                self.next_id = max(t["id"] for t in self.tasks) + 1

    def save(self):
        """
        Saves all tasks in memory to the CSV file.
        Called after every change so data is never lost.
        """
        # Make sure the data/ folder exists before writing
        os.makedirs("data", exist_ok=True)

        with open(self.DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()        # Writes the column names on the first row
            writer.writerows(self.tasks)  # Writes every task as a row

    def add_task(self, name, module, deadline, priority, status="Pending"):
        """
        Creates a new task and adds it to the list.

        Args:
            name (str): The task name e.g. 'Lab Report'
            module (str): The module code e.g. '25WSB301'
            deadline (str): Due date in YYYY-MM-DD format
            priority (str): 'High', 'Medium', or 'Low'
            status (str): Defaults to 'Pending'

        Returns:
            dict: The newly created task
        """
        # Validation — task name cannot be empty
        if not name or not name.strip():
            raise ValueError("Task name cannot be empty.")

        task = {
            "id": self.next_id,
            "name": name.strip(),
            "module": module,
            "deadline": deadline,
            "priority": priority,
            "status": status
        }

        self.tasks.append(task)   # Add to the in-memory list
        self.next_id += 1         # Increment so the next task gets a new unique id
        self.save()               # Immediately save to CSV
        return task

    def delete_task(self, task_id):
        """
        Removes a task by its id.

        Args:
            task_id (int): The id of the task to delete

        Returns:
            bool: True if deleted, False if not found
        """
        # Keep every task EXCEPT the one with the matching id
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]

        if len(self.tasks) < original_count:
            self.save()
            return True
        return False  # Nothing was deleted — id not found

    def update_task(self, task_id, **kwargs):
        """
        Updates one or more fields of an existing task.

        Args:
            task_id (int): The id of the task to update
            **kwargs: Any fields to update e.g. status='Completed'

        Returns:
            bool: True if updated, False if not found
        """
        for task in self.tasks:
            if task["id"] == task_id:
                for key, value in kwargs.items():
                    if key in self.FIELDS:  # Only update valid fields
                        task[key] = value
                self.save()
                return True
        return False  # Task not found

    def get_all(self):
        """
        Returns all tasks.

        Returns:
            list: A copy of the full task list
        """
        return list(self.tasks)

    def filter_by(self, status=None, priority=None, module=None, search=None):
        """
        Returns a filtered list of tasks based on the given criteria.
        Any criteria left as None is ignored.

        Args:
            status (str): e.g. 'Pending' or 'Completed'
            priority (str): e.g. 'High'
            module (str): e.g. '25WSB301'
            search (str): Searches task names for this text

        Returns:
            list: Tasks that match all provided filters
        """
        results = self.tasks

        if status:
            results = [t for t in results if t["status"].lower() == status.lower()]
        if priority:
            results = [t for t in results if t["priority"].lower() == priority.lower()]
        if module:
            results = [t for t in results if t["module"] == module]
        if search:
            results = [t for t in results if search.lower() in t["name"].lower()]

        return list(results)

    def get_urgency(self, deadline_str):
        """
        Returns a colour urgency level based on how close the deadline is.
        Red = due within 1 day, Amber = within 7 days, Green = more than 7 days.

        Args:
            deadline_str (str): Deadline in YYYY-MM-DD format

        Returns:
            str: 'red', 'amber', or 'green'
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
            return "green"  # If date is invalid, default to green