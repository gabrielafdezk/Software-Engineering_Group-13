from models.task_model import TaskModel


class AppController:
    """
    Middle layer between the Tkinter views and the TaskModel.
    Views should use this controller instead of accessing the CSV file directly.
    """

    def __init__(self, data_file="data/tasks.csv"):
        """
        Creates the TaskModel.
        """
        self.model = TaskModel(data_file)

    def add_task(self, name, module, deadline, priority, status="Pending"):
        """
        Adds a new task.
        Returns the new task, or an error dictionary if validation fails.
        """
        try:
            return self.model.add_task(name, module, deadline, priority, status)
        except ValueError as error:
            return {"error": str(error)}

    def delete_task(self, task_id):
        """
        Deletes a task by id.
        """
        return self.model.delete_task(task_id)

    def update_task(self, task_id, **kwargs):
        """
        Updates an existing task.
        """
        try:
            return self.model.update_task(task_id, **kwargs)
        except ValueError as error:
            return {"error": str(error)}

    def get_all_tasks(self):
        """
        Returns all tasks with urgency added.
        """
        tasks = self.model.get_all()

        for task in tasks:
            task["urgency"] = self.model.get_urgency(task["deadline"])

        return tasks

    def filter_tasks(self, status=None, priority=None, module=None, search=None):
        """
        Returns filtered tasks with urgency added.
        """
        tasks = self.model.filter_by(
            status=status,
            priority=priority,
            module=module,
            search=search
        )

        for task in tasks:
            task["urgency"] = self.model.get_urgency(task["deadline"])

        return tasks

    def get_dashboard_summary(self):
        """
        Returns summary data for the dashboard.
        """
        tasks = self.model.get_all()

        total = len(tasks)
        completed = len([
            task for task in tasks
            if task["status"].lower() == "completed"
        ])
        pending_count = total - completed

        pending_tasks = [
            task for task in tasks
            if task["status"].lower() != "completed"
        ]

        next_deadline = None

        if pending_tasks:
            next_deadline = min(
                pending_tasks,
                key=lambda task: task["deadline"]
            )

        return {
            "total": total,
            "completed": completed,
            "pending": pending_count,
            "next_deadline": next_deadline
        }

    def get_modules(self):
        """
        Returns a sorted list of unique module codes.
        """
        tasks = self.model.get_all()
        modules = list(set(task["module"] for task in tasks))

        return sorted(modules)

    def get_tasks_for_calendar(self):
        """
        Groups tasks by deadline for the calendar screen.
        """
        tasks = self.model.get_all()
        calendar_data = {}

        for task in tasks:
            deadline = task["deadline"]

            if deadline not in calendar_data:
                calendar_data[deadline] = []

            calendar_data[deadline].append(task)

        return calendar_data

    def get_urgency(self, deadline_str):
        """
        Returns the urgency colour for a deadline.
        """
        return self.model.get_urgency(deadline_str)