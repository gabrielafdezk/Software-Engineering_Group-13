import tkinter as tk
from tkinter import font as tkfont
from datetime import date, timedelta
import csv
import os


BG_PRIMARY   = "#14142a"
BG_SECONDARY = "#1a1a2e"
BG_TERTIARY  = "#0c0c14"

TEXT_PRIMARY   = "#e8e6f0"
TEXT_SECONDARY = "#9896a8"
TEXT_TERTIARY  = "#5c5a6e"

BORDER_COLOR = "#1a1a2a"

RED_FILL    = "#FCEBEB"
RED_TEXT    = "#A32D2D"
AMBER_FILL  = "#FAEEDA"
AMBER_TEXT  = "#854F0B"
GREEN_FILL  = "#EAF3DE"
GREEN_TEXT  = "#3B6D11"
BLUE_ACCENT = "#185FA5"


SAMPLE_TASKS = [
    {
        "name": "Thermodynamics",
        "module": "WSB201",
        "due_date": date.today(),
        "status": "Pending",
        "priority": "High",
    },
    {
        "name": "Group Essay Draft",
        "module": "ENG102",
        "due_date": date.today() + timedelta(days=2),
        "status": "Completed",
        "priority": "High",
    },
    {
        "name": "Maths 4",
        "module": "MATH301",
        "due_date": date.today() + timedelta(days=6),
        "status": "Completed",
        "priority": "Medium",
    },
    {
        "name": "Software Design",
        "module": "CS301",
        "due_date": date.today() + timedelta(days=10),
        "status": "Completed",
        "priority": "Low",
    },
    {
        "name": "History Essay",
        "module": "HIST110",
        "due_date": date.today() + timedelta(days=14),
        "status": "Completed",
        "priority": "Medium",
    },
]



def urgency_colors(days_left: int) -> tuple[str, str]:
    """Return (bg_color, text_color) based on days until deadline."""
    if days_left < 0:
        return RED_FILL, RED_TEXT          # overdue
    elif days_left <= 1:
        return RED_FILL, RED_TEXT          # due today / tomorrow
    elif days_left <= 3:
        return AMBER_FILL, AMBER_TEXT      # due soon
    else:
        return GREEN_FILL, GREEN_TEXT      # plenty of time


def urgency_label(days_left: int) -> str:
    """Human-readable deadline label."""
    if days_left < 0:
        return f"Overdue by {abs(days_left)}d"
    elif days_left == 0:
        return "Due today"
    elif days_left == 1:
        return "Due tomorrow"
    else:
        return f"In {days_left} days"


def load_tasks_from_csv(filepath: str = "tasks.csv") -> list[dict]:
    """
    Load tasks from a CSV file.
    Expected columns: name, module, due_date (YYYY-MM-DD), status, priority
    Falls back to SAMPLE_TASKS if the file doesn't exist.
    """
    if not os.path.exists(filepath):
        return SAMPLE_TASKS

    tasks = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row["due_date"] = date.fromisoformat(row["due_date"])
                    tasks.append(row)
                except (ValueError, KeyError):
                    continue  # skip malformed rows
    except Exception:
        return SAMPLE_TASKS

    return tasks if tasks else SAMPLE_TASKS



def make_stat_card(parent, label: str, value: str, value_color: str = TEXT_PRIMARY) -> tk.Frame:
    """Create a single stat card widget and return its frame."""
    card = tk.Frame(parent, bg=BG_SECONDARY, padx=14, pady=12)
    tk.Label(
        card,
        text=label,
        font=("Segoe UI", 10),
        bg=BG_SECONDARY,
        fg=TEXT_SECONDARY,
    ).pack(anchor="w")
    tk.Label(
        card,
        text=value,
        font=("Segoe UI", 22, "bold"),
        bg=BG_SECONDARY,
        fg=value_color,
    ).pack(anchor="w")
    return card


def make_nav_button(parent, icon: str, label: str, subtitle: str, command) -> tk.Frame:
    """Create a navigation button card."""
    frame = tk.Frame(
        parent,
        bg=BG_PRIMARY,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=14,
        pady=12,
    )
    # Highlight border via a 1px ridge — simulating a 0.5px border
    frame.config(highlightbackground=BORDER_COLOR, highlightthickness=1)

    icon_lbl = tk.Label(frame, text=icon, font=("Segoe UI", 16), bg=BG_PRIMARY, fg=TEXT_PRIMARY)
    icon_lbl.pack(anchor="w")

    title_lbl = tk.Label(
        frame, text=label, font=("Segoe UI", 12, "bold"), bg=BG_PRIMARY, fg=TEXT_PRIMARY
    )
    title_lbl.pack(anchor="w")

    sub_lbl = tk.Label(
        frame, text=subtitle, font=("Segoe UI", 10), bg=BG_PRIMARY, fg=TEXT_SECONDARY
    )
    sub_lbl.pack(anchor="w")

    # Bind hover effects and click to every child widget
    def on_enter(e):
        frame.config(bg=BG_SECONDARY)
        for child in frame.winfo_children():
            child.config(bg=BG_SECONDARY)

    def on_leave(e):
        frame.config(bg=BG_PRIMARY)
        for child in frame.winfo_children():
            child.config(bg=BG_PRIMARY)

    for widget in [frame, icon_lbl, title_lbl, sub_lbl]:
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", lambda e, cmd=command: cmd())

    return frame



class MainMenu(tk.Frame):

    def __init__(self, parent, controller=None):
        super().__init__(parent, bg=BG_TERTIARY)
        self.controller = controller
        self.tasks: list[dict] = []

        self._load_data()
        self._build_ui()


    def _load_data(self):

        if self.controller and hasattr(self.controller, "get_all_tasks"):
            self.tasks = self.controller.get_all_tasks()
        else:
            self.tasks = load_tasks_from_csv()

    def refresh(self):
        self._load_data()
        self._update_stats()
        self._update_upcoming_tasks()
        self._update_statusbar()


    def _build_ui(self):
        self.inner = tk.Frame(self, bg=BG_TERTIARY, padx=20, pady=16)
        self.inner.pack(fill="both", expand=True)

        self._build_titlebar()
        self._build_stats()
        self._build_section_label("Quick actions")
        self._build_nav_buttons()
        self._build_section_label("Upcoming deadlines")
        self._build_upcoming_tasks()
        self._build_statusbar()

    def _build_titlebar(self):
        bar = tk.Frame(
            self.inner,
            bg=BG_SECONDARY,
            padx=16,
            pady=10,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        bar.pack(fill="x", pady=(0, 12))

        # Left: name + subtitle
        left = tk.Frame(bar, bg=BG_SECONDARY)
        left.pack(side="left")
        tk.Label(
            left, text="Smart-Task", font=("Segoe UI", 18, "bold"),
            bg=BG_SECONDARY, fg=TEXT_PRIMARY,
        ).pack(anchor="w")
        tk.Label(
            left, text="Academic Project Manager", font=("Segoe UI", 10),
            bg=BG_SECONDARY, fg=TEXT_SECONDARY,
        ).pack(anchor="w")

        # Right: date
        today_str = date.today().strftime("%A, %d %b %Y")
        tk.Label(
            bar, text=today_str, font=("Segoe UI", 10),
            bg=BG_SECONDARY, fg=TEXT_SECONDARY,
        ).pack(side="right")

    def _build_stats(self):
        """Three summary stat cards in a row."""
        self.stats_frame = tk.Frame(self.inner, bg=BG_TERTIARY)
        self.stats_frame.pack(fill="x", pady=(0, 12))

        for col in range(3):
            self.stats_frame.columnconfigure(col, weight=1, uniform="stat")

        # Placeholders — filled by _update_stats()
        self._stat_cards = {}

        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.get("status") == "Completed")
        urgent = sum(
            1 for t in self.tasks
            if t.get("status") != "Completed"
            and isinstance(t.get("due_date"), date)
            and (t["due_date"] - date.today()).days <= 1
        )

        self._stat_cards["total"] = make_stat_card(
            self.stats_frame, "Total tasks", str(total)
        )
        self._stat_cards["total"].grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self._stat_cards["completed"] = make_stat_card(
            self.stats_frame, "Completed", str(completed), value_color=GREEN_TEXT
        )
        self._stat_cards["completed"].grid(row=0, column=1, sticky="nsew", padx=3)

        self._stat_cards["urgent"] = make_stat_card(
            self.stats_frame, "Overdue / urgent", str(urgent),
            value_color=RED_TEXT if urgent > 0 else TEXT_PRIMARY,
        )
        self._stat_cards["urgent"].grid(row=0, column=2, sticky="nsew", padx=(6, 0))

    def _update_stats(self):
        """Recompute and refresh stat card values in-place."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.get("status") == "Completed")
        urgent = sum(
            1 for t in self.tasks
            if t.get("status") != "Completed"
            and isinstance(t.get("due_date"), date)
            and (t["due_date"] - date.today()).days <= 1
        )

        # Update the value label (second child) of each card
        for card, val, color in [
            ("total",     str(total),     TEXT_PRIMARY),
            ("completed", str(completed), GREEN_TEXT),
            ("urgent",    str(urgent),    RED_TEXT if urgent > 0 else TEXT_PRIMARY),
        ]:
            children = self._stat_cards[card].winfo_children()
            if len(children) >= 2:
                children[1].config(text=val, fg=color)

    def _build_section_label(self, text: str):
        """Small uppercase section heading."""
        tk.Label(
            self.inner,
            text=text.upper(),
            font=("Segoe UI", 9, "bold"),
            bg=BG_TERTIARY,
            fg=TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 6))

    def _build_nav_buttons(self):
        """2×2 grid of navigation buttons."""
        self.nav_frame = tk.Frame(self.inner, bg=BG_TERTIARY)
        self.nav_frame.pack(fill="x", pady=(0, 14))
        for col in range(2):
            self.nav_frame.columnconfigure(col, weight=1, uniform="nav")

        buttons = [
            ("＋", "Add task",          "Create a new assignment",     self._on_add_task),
            ("☰",  "View and edits tasks",    "Browse and edit tasks",       self._on_view_tasks),
            ("⌕",  "Search & filter",   "Search and filter tasks by priority",self._on_search),
            ("🗓",  "Calendar",  "View your calendar",         self._on_deadlines),
            ("⏱",  "Timer",          "Pomodoro study timer",         self._on_timer),
        ]

        for idx, (icon, label, subtitle, cmd) in enumerate(buttons):
            row, col = divmod(idx, 2)
            pad_x = (0, 6) if col == 0 else (6, 0)
            btn = make_nav_button(self.nav_frame, icon, label, subtitle, cmd)
            btn.grid(row=row, column=col, sticky="nsew", padx=pad_x, pady=(0, 8))

    def _build_upcoming_tasks(self):
        """Scrollable list of upcoming (pending) tasks, sorted by due date."""
        self.upcoming_outer = tk.Frame(
            self.inner,
            bg=BG_PRIMARY,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        self.upcoming_outer.pack(fill="x", pady=(0, 12))
        self._task_rows_frame = tk.Frame(self.upcoming_outer, bg=BG_PRIMARY)
        self._task_rows_frame.pack(fill="x")
        self._populate_task_rows()

    def _populate_task_rows(self):
        """Clear and redraw all task rows."""
        for widget in self._task_rows_frame.winfo_children():
            widget.destroy()

        pending = sorted(
            [t for t in self.tasks if t.get("status") != "Completed"
             and isinstance(t.get("due_date"), date)],
            key=lambda t: t["due_date"],
        )

        if not pending:
            tk.Label(
                self._task_rows_frame,
                text="No upcoming tasks — nice work!",
                font=("Segoe UI", 11),
                bg=BG_PRIMARY,
                fg=TEXT_SECONDARY,
                pady=16,
            ).pack()
            return

        show = pending[:4]
        for idx, task in enumerate(show):
            days_left = (task["due_date"] - date.today()).days
            bg_color, text_color = urgency_colors(days_left)
            label_str = urgency_label(days_left)
            self._add_task_row(task, label_str, text_color, idx, len(show))

        if len(pending) > 4:
            remaining = len(pending) - 4
            see_all = tk.Label(
                self._task_rows_frame,
                text=f"View all {len(pending)} pending tasks →",
                font=("Segoe UI", 10),
                bg=BG_PRIMARY,
                fg=BLUE_ACCENT,
                pady=8,
                cursor="hand2",
            )
            see_all.pack()
            see_all.bind("<Button-1>", lambda e: self._on_view_tasks())

    def _add_task_row(self, task: dict, due_label: str, dot_color: str, idx: int, total: int):
        row_bg = BG_PRIMARY if idx % 2 == 0 else BG_SECONDARY

        row = tk.Frame(
            self._task_rows_frame,
            bg=row_bg,
            padx=14,
            pady=9,
        )
        row.pack(fill="x")

        if idx < total - 1:
            sep = tk.Frame(self._task_rows_frame, bg=BORDER_COLOR, height=1)
            sep.pack(fill="x")

        dot_canvas = tk.Canvas(row, width=10, height=10, bg=row_bg, highlightthickness=0)
        dot_canvas.pack(side="left", padx=(0, 10))
        dot_canvas.create_oval(1, 1, 9, 9, fill=dot_color, outline="")

        tk.Label(
            row,
            text=task.get("name", "Unnamed task"),
            font=("Segoe UI", 11),
            bg=row_bg,
            fg=TEXT_PRIMARY,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        # Module badge
        module = task.get("module", "")
        if module:
            badge = tk.Label(
                row,
                text=module,
                font=("Segoe UI", 9),
                bg=BG_TERTIARY,
                fg=TEXT_SECONDARY,
                padx=6,
                pady=2,
            )
            badge.pack(side="left", padx=(4, 8))

        # Due date label
        tk.Label(
            row,
            text=due_label,
            font=("Segoe UI", 10),
            bg=row_bg,
            fg=dot_color,
        ).pack(side="right")

    def _update_upcoming_tasks(self):
        self._populate_task_rows()

    def _build_statusbar(self):
        self.status_bar = tk.Frame(
            self.inner,
            bg=BG_SECONDARY,
            padx=12,
            pady=8,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        self.status_bar.pack(fill="x")

        self._status_left = tk.Label(
            self.status_bar,
            text="Last saved: just now",
            font=("Segoe UI", 10),
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
        )
        self._status_left.pack(side="left")

        task_count = len(self.tasks)
        self._status_right = tk.Label(
            self.status_bar,
            text=f"tasks.csv · {task_count} records",
            font=("Segoe UI", 10),
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
        )
        self._status_right.pack(side="right")

    def _update_statusbar(self):
        self._status_right.config(text=f"tasks.csv · {len(self.tasks)} records")


    def _on_add_task(self):
        if self.controller and hasattr(self.controller, "show_frame"):
            self.controller.show_frame("AddTask")
        else:
            tk.messagebox.showinfo("Navigation", "Navigate to: Add Task")

    def _on_view_tasks(self):
        if self.controller and hasattr(self.controller, "show_frame"):
            self.controller.show_frame("TaskList")
        else:
            tk.messagebox.showinfo("Navigation", "Navigate to: View All Tasks")

    def _on_search(self):
        if self.controller and hasattr(self.controller, "show_frame"):
            self.controller.show_frame("SearchFilter")
        else:
            tk.messagebox.showinfo("Navigation", "Navigate to: Search & Filter")

    def _on_deadlines(self):
        if self.controller and hasattr(self.controller, "show_frame"):
            self.controller.show_frame("DeadlineTracker")
        else:
            tk.messagebox.showinfo("Navigation", "Navigate to: Calendar")
    def _on_timer(self):
        if self.controller and hasattr(self.controller, "show_frame"):
            self.controller.show_frame("Timer")
        else:
            tk.messagebox.showinfo("Navigation", "Navigate to: Timer")


def main():
    root = tk.Tk()
    root.title("SmartTask – Main Menu")
    root.geometry("700x740")
    root.configure(bg=BG_TERTIARY)
    root.resizable(True, True)

    root.update_idletasks()
    w, h = 700, 740
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    menu = MainMenu(root, controller=None)
    menu.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    import tkinter.messagebox
    main()
