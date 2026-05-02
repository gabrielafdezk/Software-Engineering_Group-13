import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class TaskFormView:
    def __init__(self, root, controller):
        """
        Task Form View for adding, editing, and searching tasks.
        """
        self.root = root
        self.controller = controller
        self.selected_task_id = None

        self.root.title("Add / Edit / Search Tasks")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20)

        self.form_frame = tk.Frame(self.main_frame)
        self.form_frame.grid(row=0, column=0, padx=20)

        self.list_frame = tk.Frame(self.main_frame)
        self.list_frame.grid(row=0, column=1, padx=20)

        tk.Label(self.form_frame, text="Task Name").grid(row=0, column=0, pady=5)
        self.name_entry = tk.Entry(self.form_frame)
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.form_frame, text="Module").grid(row=1, column=0, pady=5)
        self.module_entry = tk.Entry(self.form_frame)
        self.module_entry.grid(row=1, column=1, pady=5)

        tk.Label(self.form_frame, text="Deadline (YYYY-MM-DD)").grid(row=2, column=0, pady=5)
        self.deadline_entry = tk.Entry(self.form_frame)
        self.deadline_entry.grid(row=2, column=1, pady=5)

        tk.Label(self.form_frame, text="Priority").grid(row=3, column=0, pady=5)
        self.priority_entry = ttk.Combobox(
            self.form_frame,
            values=["High", "Medium", "Low"],
            state="readonly"
        )
        self.priority_entry.grid(row=3, column=1, pady=5)
        self.priority_entry.set("Medium")

        tk.Label(self.form_frame, text="Status").grid(row=4, column=0, pady=5)
        self.status_entry = ttk.Combobox(
            self.form_frame,
            values=["Pending", "Completed"],
            state="readonly"
        )
        self.status_entry.grid(row=4, column=1, pady=5)
        self.status_entry.set("Pending")

        self.add_button = tk.Button(
            self.form_frame,
            text="Add Task",
            command=self.add_task
        )
        self.add_button.grid(row=5, column=0, pady=10)

        self.update_button = tk.Button(
            self.form_frame,
            text="Update Task",
            command=self.update_task
        )
        self.update_button.grid(row=5, column=1, pady=10)

        self.clear_button = tk.Button(
            self.form_frame,
            text="Clear Form",
            command=self.clear_form
        )
        self.clear_button.grid(row=6, column=0, columnspan=2, pady=5)

        tk.Label(self.list_frame, text="Search Tasks").pack()

        self.search_entry = tk.Entry(self.list_frame, width=35)
        self.search_entry.pack(pady=5)

        self.search_button = tk.Button(
            self.list_frame,
            text="Search",
            command=self.search_tasks
        )
        self.search_button.pack(pady=2)

        self.clear_search_button = tk.Button(
            self.list_frame,
            text="Clear Search",
            command=self.load_tasks
        )
        self.clear_search_button.pack(pady=2)

        tk.Label(self.list_frame, text="Existing Tasks").pack(pady=(10, 0))

        self.task_listbox = tk.Listbox(self.list_frame, width=40, height=12)
        self.task_listbox.pack(pady=5)

        self.task_listbox.bind("<<ListboxSelect>>", self.load_selected_task)

        self.tasks = []
        self.load_tasks()

    def remove_urgency_field(self):
        """
        Remove urgency from task dictionaries because it is only used for display,
        not saved in the CSV file.
        """
        for task in self.tasks:
            task.pop("urgency", None)

    def load_tasks(self):
        """
        Load all tasks from the controller and display them in the listbox.
        """
        self.task_listbox.delete(0, tk.END)
        self.tasks = self.controller.get_all_tasks()
        self.remove_urgency_field()

        for task in self.tasks:
            display_text = f"{task['id']} - {task['name']} ({task['module']})"
            self.task_listbox.insert(tk.END, display_text)

    def search_tasks(self):
        """
        Search tasks by task name using the controller.
        """
        search_text = self.search_entry.get()

        self.task_listbox.delete(0, tk.END)
        self.tasks = self.controller.filter_tasks(search=search_text)
        self.remove_urgency_field()

        for task in self.tasks:
            display_text = f"{task['id']} - {task['name']} ({task['module']})"
            self.task_listbox.insert(tk.END, display_text)

    def load_selected_task(self, event):
        """
        Load the selected task details into the form for editing.
        """
        selected = self.task_listbox.curselection()

        if not selected:
            return

        index = selected[0]
        task = self.tasks[index]

        self.selected_task_id = task["id"]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, task["name"])

        self.module_entry.delete(0, tk.END)
        self.module_entry.insert(0, task["module"])

        self.deadline_entry.delete(0, tk.END)
        self.deadline_entry.insert(0, task["deadline"])

        self.priority_entry.set(task["priority"])
        self.status_entry.set(task["status"])

    def add_task(self):
        """
        Add a new task using the form values.
        """
        name = self.name_entry.get()
        module = self.module_entry.get()
        deadline = self.deadline_entry.get()
        priority = self.priority_entry.get()
        status = self.status_entry.get()

        result = self.controller.add_task(name, module, deadline, priority, status)

        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Error", result["error"])
        else:
            messagebox.showinfo("Success", "Task added!")
            self.clear_form()
            self.load_tasks()

    def update_task(self):
        """
        Update the selected task using the form values.
        """
        if self.selected_task_id is None:
            messagebox.showerror("Error", "Please select a task to edit first.")
            return

        result = self.controller.update_task(
            self.selected_task_id,
            name=self.name_entry.get(),
            module=self.module_entry.get(),
            deadline=self.deadline_entry.get(),
            priority=self.priority_entry.get(),
            status=self.status_entry.get()
        )

        if result:
            messagebox.showinfo("Success", "Task updated!")
            self.clear_form()
            self.load_tasks()
        else:
            messagebox.showerror("Error", "Task could not be updated.")

    def clear_form(self):
        """
        Clear all form fields and reset dropdowns.
        """
        self.selected_task_id = None

        self.name_entry.delete(0, tk.END)
        self.module_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)

        self.priority_entry.set("Medium")
        self.status_entry.set("Pending")

        self.task_listbox.selection_clear(0, tk.END)