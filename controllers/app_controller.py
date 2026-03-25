from models.task_model import TaskModel

class AppController:
    """
    The AppController acts as the middleman between the Views (UI screens)
    and the TaskModel (data layer). All user actions from the UI flow through
    here — the Views never talk to the Model directly.
    """

    def __init__(self):
        """
        Constructor — runs when AppController() is called.
        Creates an instance of TaskModel so we can use its methods.
        """
        self.model = TaskModel()

    # -------------------------
    # TASK CRUD OPERATIONS
    # -------------------------

    def add_task(self, name, module, deadline, priority, status="Pending"):
        """
        Adds a new task. Called when the user submits the Add Task form.

        Args:
            name (str): Task name e.g. 'Lab Report'
            module (str): Module code e.g. '25WSB301'
            deadline (str): Due date in YYYY-MM-DD format
            priority (str): 'High', 'Medium', or 'Low'
            status (str): Defaults to 'Pending'

        Returns:
            dict: The newly created task, or None if validation failed
        """
        try:
            task = self.model.add_task(name, module, deadline, priority, status)
            return task
        except ValueError as e:
            # Return the error message so the View can show it to the user
            return {"error": str(e)}

    def delete_task(self, task_id):
        """
        Deletes a task by its id. Called when the user clicks Delete.

        Args:
            task_id (int): The id of the task to delete

        Returns:
            bool: True if deleted, False if not found
        """
        return self.model.delete_task(task_id)

    def update_task(self, task_id, **kwargs):
        """
        Updates one or more fields of a task. Called when the user edits a task.

        Args:
            task_id (int): The id of the task to update
            **kwargs: Fields to update e.g. status='Completed', priority='High'

        Returns:
            bool: True if updated, False if not found
        """
        return self.model.update_task(task_id, **kwargs)

    def get_all_tasks(self):
        """
        Returns all tasks. Called when the Timeline or Dashboard loads.

        Returns:
            list: All tasks with urgency colour added to each
        """
        tasks = self.model.get_all()
        # Add urgency colour to each task so the View can show traffic lights
        for task in tasks:
            task["urgency"] = self.model.get_urgency(task["deadline"])
        return tasks

    # -------------------------
    # SEARCH & FILTER
    # -------------------------

    def filter_tasks(self, status=None, priority=None, module=None, search=None):
        """
        Returns a filtered list of tasks. Called when the user uses the
        filter buttons or search bar.

        Args:
            status (str): e.g. 'Pending' or 'Completed'
            priority (str): e.g. 'High'
            module (str): e.g. '25WSB301'
            search (str): Text to search for in task names

        Returns:
            list: Filtered tasks with urgency colour added
        """
        tasks = self.model.filter_by(status=status, priority=priority,
                                     module=module, search=search)
        for task in tasks:
            task["urgency"] = self.model.get_urgency(task["deadline"])
        return tasks

    # -------------------------
    # DASHBOARD SUMMARY
    # -------------------------

    def get_dashboard_summary(self):
        """
        Returns summary data for the Dashboard view.
        Shows total tasks, completed count, and the next upcoming deadline.

        Returns:
            dict: Summary with total, completed, and next_deadline keys
        """
        tasks = self.model.get_all()
        total = len(tasks)
        completed = len([t for t in tasks if t["status"].lower() == "completed"])

        # Find the next upcoming deadline from pending tasks
        pending = [t for t in tasks if t["status"].lower() != "completed"]
        next_deadline = None
        if pending:
            next_deadline = min(pending, key=lambda t: t["deadline"])

        return {
            "total": total,
            "completed": completed,
            "next_deadline": next_deadline
        }

    # -------------------------
    # MODULES
    # -------------------------

    def get_modules(self):
        """
        Returns a list of all unique module codes from existing tasks.
        Used to populate the sidebar module list.

        Returns:
            list: Unique module codes e.g. ['25WSB301', '25MAT102']
        """
        tasks = self.model.get_all()
        modules = list(set(t["module"] for t in tasks))
        return sorted(modules)

    # -------------------------
    # URGENCY
    # -------------------------

    def get_urgency(self, deadline_str):
        """
        Returns the urgency colour for a given deadline.
        Used by Views to show traffic light colours.

        Args:
            deadline_str (str): Deadline in YYYY-MM-DD format

        Returns:
            str: 'red', 'amber', or 'green'
        """
        return self.model.get_urgency(deadline_str)