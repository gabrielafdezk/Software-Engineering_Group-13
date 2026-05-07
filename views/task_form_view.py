import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


FONT_NAME = "Segoe UI"

BG_PRIMARY = "#0c0c14"
BG_SECONDARY = "#1a1a2e"
BG_CARD = "#14142a"
TEXT_PRIMARY = "#e8e6f0"
TEXT_SECONDARY = "#9896a8"
BORDER_COLOR = "#1a1a2a"
BLUE_ACCENT = "#185FA5"


class TaskFormView(tk.Frame):
    def __init__(self, parent, controller):
        """
        Task Form View for adding, editing, and searching tasks.
        Designed to integrate as a page inside the main application.
        """
        super().__init__(parent, bg=BG_PRIMARY)

        self.controller = controller
        self.selected_task_id = None
        self.tasks = []

        self._build_ui()
        self.load_tasks()

    def _build_ui(self):
        self.inner = tk.Frame(self, bg=BG_PRIMARY, padx=24, pady=20)
        self.inner.pack(fill="both", expand=True)

        # Title bar
        title_bar = tk.Frame(
            self.inner,
            bg=BG_SECONDARY,
            padx=18,
            pady=12,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        title_bar.pack(fill="x", pady=(0, 16))

        tk.Label(
            title_bar,
            text="Add / Edit / Search Tasks",
            font=(FONT_NAME, 20, "bold"),
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY
        ).pack(anchor="w")

        tk.Label(
            title_bar,
            text="Create, update and find academic tasks",
            font=(FONT_NAME, 10),
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY
        ).pack(anchor="w")

        # Main content
        content = tk.Frame(self.inner, bg=BG_PRIMARY)
        content.pack(fill="both", expand=True)

        content.columnconfigure(0, weight=1, uniform="content")
        content.columnconfigure(1, weight=1, uniform="content")
        content.rowconfigure(0, weight=1)

        # Left card: form
        self.form_card = tk.Frame(
            content,
            bg=BG_CARD,
            padx=22,
            pady=20,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        self.form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Right card: search/list
        self.list_card = tk.Frame(
            content,
            bg=BG_CARD,
            padx=22,
            pady=20,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        self.list_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._build_form()
        self._build_search_list()

    def _label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            font=(FONT_NAME, 11, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY
        )

    def _entry(self, parent):
        return tk.Entry(
            parent,
            font=(FONT_NAME, 11),
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat"
        )

    def _button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT_NAME, 10, "bold"),
            bg=BLUE_ACCENT,
            fg="white",
            activebackground="#2474C2",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )

    def _build_form(self):
        tk.Label(
            self.form_card,
            text="Task Details",
            font=(FONT_NAME, 15, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))

        self.form_card.columnconfigure(1, weight=1)

        self._label(self.form_card, "Task Name").grid(row=1, column=0, sticky="w", pady=8)
        self.name_entry = self._entry(self.form_card)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=8, ipady=6)

        self._label(self.form_card, "Module").grid(row=2, column=0, sticky="w", pady=8)
        self.module_entry = self._entry(self.form_card)
        self.module_entry.grid(row=2, column=1, sticky="ew", pady=8, ipady=6)

        self._label(self.form_card, "Deadline").grid(row=3, column=0, sticky="w", pady=8)
        self.deadline_entry = self._entry(self.form_card)
        self.deadline_entry.grid(row=3, column=1, sticky="ew", pady=8, ipady=6)

        tk.Label(
            self.form_card,
            text="YYYY-MM-DD",
            font=(FONT_NAME, 9),
            bg=BG_CARD,
            fg=TEXT_SECONDARY
        ).grid(row=4, column=1, sticky="w", pady=(0, 6))

        self._label(self.form_card, "Priority").grid(row=5, column=0, sticky="w", pady=8)
        self.priority_entry = ttk.Combobox(
            self.form_card,
            values=["High", "Medium", "Low"],
            state="readonly",
            font=(FONT_NAME, 10)
        )
        self.priority_entry.grid(row=5, column=1, sticky="ew", pady=8, ipady=4)
        self.priority_entry.set("Medium")

        self._label(self.form_card, "Status").grid(row=6, column=0, sticky="w", pady=8)
        self.status_entry = ttk.Combobox(
            self.form_card,
            values=["Pending", "Completed"],
            state="readonly",
            font=(FONT_NAME, 10)
        )
        self.status_entry.grid(row=6, column=1, sticky="ew", pady=8, ipady=4)
        self.status_entry.set("Pending")

        button_row = tk.Frame(self.form_card, bg=BG_CARD)
        button_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(24, 8))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)
        button_row.columnconfigure(2, weight=1)

        self._button(button_row, "Add Task", self.add_task).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(button_row, "Update Task", self.update_task).grid(row=0, column=1, sticky="ew", padx=6)
        self._button(button_row, "Delete Task", self.delete_task).grid(row=0, column=2, sticky="ew", padx=(6, 0))


        clear_btn = tk.Button(
            self.form_card,
            text="Clear Form",
            command=self.clear_form,
            font=(FONT_NAME, 10, "bold"),
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY,
            activebackground=BG_PRIMARY,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        clear_btn.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _build_search_list(self):
        tk.Label(
            self.list_card,
            text="Search Tasks",
            font=(FONT_NAME, 15, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))

        self.search_entry = self._entry(self.list_card)
        self.search_entry.pack(fill="x", ipady=6, pady=(0, 10))

        search_buttons = tk.Frame(self.list_card, bg=BG_CARD)
        search_buttons.pack(fill="x", pady=(0, 16))
        search_buttons.columnconfigure(0, weight=1)
        search_buttons.columnconfigure(1, weight=1)

        self._button(search_buttons, "Search", self.search_tasks).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(search_buttons, "Clear Search", self.load_tasks).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        tk.Label(
            self.list_card,
            text="Existing Tasks",
            font=(FONT_NAME, 13, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))

        self.task_listbox = tk.Listbox(
            self.list_card,
            height=16,
            font=(FONT_NAME, 10),
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY,
            selectbackground=BLUE_ACCENT,
            selectforeground="white",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            activestyle="none"
        )
        self.task_listbox.pack(fill="both", expand=True)

        self.task_listbox.bind("<<ListboxSelect>>", self.load_selected_task)

    def remove_urgency_field(self):
        for task in self.tasks:
            task.pop("urgency", None)

    def load_tasks(self):
        self.search_entry.delete(0, tk.END)
        self.task_listbox.delete(0, tk.END)

        self.tasks = self.controller.get_all_tasks()
        self.remove_urgency_field()

        for task in self.tasks:
            display_text = f"{task['id']} - {task['name']} ({task['module']})"
            self.task_listbox.insert(tk.END, display_text)

    def search_tasks(self):
        search_text = self.search_entry.get()

        self.task_listbox.delete(0, tk.END)
        self.tasks = self.controller.filter_tasks(search=search_text)
        self.remove_urgency_field()

        for task in self.tasks:
            display_text = f"{task['id']} - {task['name']} ({task['module']})"
            self.task_listbox.insert(tk.END, display_text)

    def load_selected_task(self, event):
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
        result = self.controller.add_task(
            self.name_entry.get(),
            self.module_entry.get(),
            self.deadline_entry.get(),
            self.priority_entry.get(),
            self.status_entry.get()
        )

        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Error", result["error"])
        else:
            messagebox.showinfo("Success", "Task added!")
            self.clear_form()
            self.load_tasks()

    def update_task(self):
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

        if isinstance(result, dict) and "error" in result:
            messagebox.showerror("Error", result["error"])
        elif result:
            messagebox.showinfo("Success", "Task updated!")
            self.clear_form()
            self.load_tasks()
        else:
            messagebox.showerror("Error", "Task could not be updated.")
    
    def delete_task(self):
        if self.selected_task_id is None:
            messagebox.showerror("Error", "Please select a task to delete first.")
            return

        confirm = messagebox.askyesno(
            "Delete Task",
            "Are you sure you want to delete this task?"
        )

        if not confirm:
            return

        result = self.controller.delete_task(self.selected_task_id)

        if result:
            messagebox.showinfo("Success", "Task deleted!")
            self.clear_form()
            self.load_tasks()
        else:
            messagebox.showerror("Error", "Task could not be deleted.")


    def clear_form(self):
        self.selected_task_id = None

        self.name_entry.delete(0, tk.END)
        self.module_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)

        self.priority_entry.set("Medium")
        self.status_entry.set("Pending")

        self.task_listbox.selection_clear(0, tk.END)