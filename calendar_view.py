import tkinter as tk
from datetime import date, timedelta
from tkinter import font as tkfont
from tkinter import ttk


FONT_NAME = "Segoe UI"

# Dark palette — matches the rest of Smart-Task
BG = "#0c0c14"               # main area / out-of-month cells
SURFACE = "#14142a"          # sidebar, in-month cells
SURFACE_2 = "#1a1a2e"        # top bar
BORDER = "#1a1a2a"           # cell borders
TEXT = "#e8e6f0"             # primary text
MUTED = "#9896a8"            # secondary text
TODAY_BG = "#1a3268"         # today cell background
TODAY_FG = "#dff1ff"         # day number inside today
OUT_OF_MONTH_FG = "#4a4a5a"  # dimmed previous/next-month day numbers

# Aliases so the existing code reads naturally with the dark palette
BLUE = TEXT
LIGHT_BLUE = TODAY_BG
SIDEBAR_BG = SURFACE
SIDEBAR_TEXT = TEXT
MUTED_TEXT = MUTED
GRID_LINE = BORDER

PRIORITY_COLOURS = {
    "high": {
        "bg": "#3a1a1a",
        "border": "#E53935",
        "text": "#fca5a5",
    },
    "medium": {
        "bg": "#3a2a14",
        "border": "#F4B400",
        "text": "#fcd34d",
    },
    "low": {
        "bg": "#16321a",
        "border": "#4ECB3F",
        "text": "#86efac",
    },
}


class CalendarTask:
    def __init__(self, title, task_date, start_hour, duration, priority):
        self.title = title
        self.task_date = task_date
        self.start_hour = start_hour
        self.duration = duration
        self.priority = priority


class CalendarView(tk.Frame):
    """
    Monthly calendar embedded in the main app's screen stack.
    Same structure as Viv's original CalendarWindow — internal sidebar with
    weekly task list, top bar with month nav and search, and a six-row
    month grid — just hosted as a Frame inside the parent container instead
    of as a separate Toplevel popup.
    """

    def __init__(self, parent, controller=None, on_home=None):
        tk.Frame.__init__(self, parent, bg=BG)

        self.today = date.today()
        self.current_date = self.today
        self.on_home = on_home
        self.controller = controller
        self.search_text = tk.StringVar()
        self.search_text.trace("w", self.refresh_from_search)

        self.tasks = self.load_tasks()

        self.force_segoe_ui_font()
        self.create_styles()
        self.create_layout()
        self.refresh()

    def force_segoe_ui_font(self):
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family=FONT_NAME, size=10)

        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family=FONT_NAME, size=10)

        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(family=FONT_NAME, size=10)

        menu_font = tkfont.nametofont("TkMenuFont")
        menu_font.configure(family=FONT_NAME, size=10)

        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(family=FONT_NAME, size=10, weight="bold")

        self.option_add("*Font", (FONT_NAME, 10))

    def create_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Nav.TButton",
            font=(FONT_NAME, 12),
            padding=(14, 7),
            background=SURFACE_2,
            foreground=TEXT,
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Nav.TButton",
            background=[("active", SURFACE), ("pressed", SURFACE)],
            foreground=[("active", "#ffffff")],
        )

        style.configure(
            "Today.TButton",
            font=(FONT_NAME, 11, "bold"),
            padding=(18, 7),
            background=SURFACE_2,
            foreground=TEXT,
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Today.TButton",
            background=[("active", SURFACE), ("pressed", SURFACE)],
            foreground=[("active", "#ffffff")],
        )

        style.configure("TButton", font=(FONT_NAME, 10))
        style.configure("TEntry", font=(FONT_NAME, 12))
        style.configure(
            "Minimal.Vertical.TScrollbar",
            gripcount=0,
            background=MUTED,
            darkcolor=MUTED,
            lightcolor=MUTED,
            troughcolor=SURFACE,
            bordercolor=SURFACE,
            arrowcolor=SURFACE,
            relief="flat",
            borderwidth=0,
            width=10,
        )
        style.map(
            "Minimal.Vertical.TScrollbar",
            background=[("active", "#b8b3c8"), ("pressed", "#7a7888")],
        )
        style.configure(
            "Sidebar.TButton",
            font=(FONT_NAME, 10, "bold"),
            padding=(12, 6),
            background=SIDEBAR_BG,
            foreground=SIDEBAR_TEXT,
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Sidebar.TButton",
            background=[("active", SURFACE_2), ("pressed", BG)],
            foreground=[("active", "white")],
        )

    def create_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=310)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.main_area = tk.Frame(self, bg=BG)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.rowconfigure(1, weight=1)

        self.create_sidebar()
        self.create_top_bar()

        self.calendar_area = tk.Frame(self.main_area, bg=BG)
        self.calendar_area.grid(row=1, column=0, sticky="nsew")
        self.calendar_area.columnconfigure(0, weight=1)
        self.calendar_area.rowconfigure(0, weight=1)

    def create_sidebar(self):
        header = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        header.pack(fill="x", padx=28, pady=(32, 26))

        self.month_title = tk.Label(
            header,
            text="",
            font=(FONT_NAME, 25, "bold"),
            fg=SIDEBAR_TEXT,
            bg=SIDEBAR_BG,
        )
        self.month_title.pack(side="left", anchor="w")

        self.home_button = tk.Canvas(
            header,
            width=42,
            height=42,
            bg=SIDEBAR_BG,
            highlightthickness=0,
            cursor="hand2",
        )
        self.home_button.pack(side="right", padx=(12, 0))
        self.draw_home_icon(TEXT)
        self.home_button.bind("<Button-1>", lambda event: self.go_home())
        self.home_button.bind("<Enter>", lambda event: self.draw_home_icon("#FFFFFF"))
        self.home_button.bind("<Leave>", lambda event: self.draw_home_icon(TEXT))

        self.task_canvas = tk.Canvas(
            self.sidebar,
            bg=SIDEBAR_BG,
            highlightthickness=0,
            bd=0,
        )
        self.task_scrollbar = ttk.Scrollbar(
            self.sidebar,
            orient="vertical",
            command=self.task_canvas.yview,
            style="Minimal.Vertical.TScrollbar",
        )
        self.task_list = tk.Frame(self.task_canvas, bg=SIDEBAR_BG)

        self.task_list_window = self.task_canvas.create_window(
            (0, 0),
            window=self.task_list,
            anchor="nw",
        )

        self.task_canvas.configure(yscrollcommand=self.task_scrollbar.set)
        self.task_canvas.pack(side="left", fill="both", expand=True, padx=(28, 0), pady=(0, 18))
        self.task_scrollbar.pack(side="right", fill="y", padx=(4, 8), pady=(0, 18))

        self.task_list.bind("<Configure>", self.update_task_scroll_area)
        self.task_canvas.bind("<Configure>", self.resize_task_list)
        self.task_canvas.bind_all("<MouseWheel>", self.scroll_task_list)

    def create_top_bar(self):
        top_bar = tk.Frame(self.main_area, bg=SURFACE_2, height=72)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_propagate(False)
        top_bar.columnconfigure(1, weight=1)

        navigation = tk.Frame(top_bar, bg=SURFACE_2)
        navigation.grid(row=0, column=0, sticky="w", padx=14, pady=16)

        ttk.Button(navigation, text="<", style="Nav.TButton", command=lambda: self.change_month(-1)).pack(side="left")
        ttk.Button(navigation, text="Today", style="Today.TButton", command=self.go_to_today).pack(side="left", padx=1)
        ttk.Button(navigation, text=">", style="Nav.TButton", command=lambda: self.change_month(1)).pack(side="left")

        # Title sits next to the nav buttons so it always has room — the
        # middle column is just a spacer that absorbs any leftover space.
        tk.Label(
            navigation,
            text="Monthly Calendar",
            font=(FONT_NAME, 13, "bold"),
            fg=TEXT,
            bg=SURFACE_2,
        ).pack(side="left", padx=(20, 0))

        search_entry = tk.Entry(
            top_bar,
            textvariable=self.search_text,
            font=(FONT_NAME, 12),
            bg=SURFACE,
            fg=TEXT,
            relief="flat",
            width=20,
            insertbackground=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=MUTED,
        )
        search_entry.grid(row=0, column=2, sticky="e", padx=16, pady=16, ipady=8)
        search_entry.insert(0, "")

    def load_tasks(self):
        """Load tasks from the controller and convert them to CalendarTask objects."""
        if self.controller is None:
            return []

        tasks = []
        for task_dict in self.controller.get_all_tasks():
            try:
                task_date = date.fromisoformat(task_dict.get("deadline", ""))
            except (ValueError, TypeError):
                continue

            tasks.append(CalendarTask(
                title=task_dict.get("name", ""),
                task_date=task_date,
                start_hour=None,
                duration=None,
                priority=(task_dict.get("priority") or "low").lower(),
            ))
        return tasks

    def refresh_from_search(self, name, index, mode):
        # Search-typing doesn't need a CSV reload — just redraw against
        # the in-memory task list.
        self._redraw()

    def refresh(self):
        """Reload tasks from the controller and redraw."""
        self.tasks = self.load_tasks()
        self._redraw()

    def _redraw(self):
        self.month_title.config(text=self.current_date.strftime("%B %Y"))
        self.draw_sidebar_week_tasks()

        for widget in self.calendar_area.winfo_children():
            widget.destroy()

        self.draw_month_view()

    def go_to_today(self):
        self.current_date = self.today
        self.refresh()

    def go_home(self):
        if self.on_home is not None:
            self.on_home()

    def draw_home_icon(self, colour):
        self.home_button.delete("all")
        self.home_button.create_line(
            8, 22,
            21, 10,
            34, 22,
            fill=colour,
            width=3,
            capstyle="round",
            joinstyle="round",
        )
        self.home_button.create_line(
            12, 21,
            12, 34,
            30, 34,
            30, 21,
            fill=colour,
            width=3,
            capstyle="round",
            joinstyle="round",
        )
        self.home_button.create_line(
            18, 34,
            18, 26,
            24, 26,
            24, 34,
            fill=colour,
            width=3,
            capstyle="round",
            joinstyle="round",
        )

    def change_month(self, direction):
        new_month = self.current_date.month + direction
        new_year = self.current_date.year

        if new_month < 1:
            new_month = 12
            new_year = new_year - 1
        elif new_month > 12:
            new_month = 1
            new_year = new_year + 1

        last_day = self.last_day_of_month(new_year, new_month)
        new_day = min(self.current_date.day, last_day)
        self.current_date = self.current_date.replace(year=new_year, month=new_month, day=new_day)
        self.refresh()

    def choose_date(self, selected_date):
        self.current_date = selected_date
        self.refresh()

    def matching_tasks(self):
        search = self.search_text.get().strip().lower()

        if search == "":
            return self.tasks

        matches = []
        for task in self.tasks:
            if search in task.title.lower():
                matches.append(task)

        return matches

    def draw_sidebar_week_tasks(self):
        for widget in self.task_list.winfo_children():
            widget.destroy()
        self.task_canvas.yview_moveto(0)

        week_start = self.current_date - timedelta(days=self.current_date.weekday())
        week_end = week_start + timedelta(days=6)
        tasks = []

        for task in self.matching_tasks():
            if week_start <= task.task_date <= week_end:
                tasks.append(task)

        tasks = sorted(tasks, key=lambda item: (item.task_date, item.start_hour is None, item.start_hour or 0))

        if len(tasks) == 0:
            tk.Label(
                self.task_list,
                text="No tasks this week",
                font=(FONT_NAME, 13),
                fg=MUTED_TEXT,
                bg=SIDEBAR_BG,
            ).pack(anchor="w", pady=10)
            return

        groups = {}
        for task in tasks:
            if task.task_date not in groups:
                groups[task.task_date] = []
            groups[task.task_date].append(task)

        for task_date in sorted(groups.keys()):
            if task_date == self.today:
                title = "TODAY"
            else:
                title = task_date.strftime("%A").upper()

            tk.Label(
                self.task_list,
                text=title + " " + task_date.strftime("%d/%m/%y"),
                font=(FONT_NAME, 12, "bold"),
                fg=BLUE if task_date == self.today else MUTED_TEXT,
                bg=SIDEBAR_BG,
            ).pack(anchor="w", pady=(12, 5))

            for task in groups[task_date]:
                row = tk.Frame(self.task_list, bg=SIDEBAR_BG)
                row.pack(fill="x", pady=4)

                dot = tk.Canvas(
                    row,
                    width=12,
                    height=12,
                    bg=SIDEBAR_BG,
                    highlightthickness=0,
                )
                dot.create_oval(2, 2, 10, 10, fill=self.priority_border(task.priority), outline="")
                dot.pack(side="left", padx=(0, 10))

                tk.Label(
                    row,
                    text=task.title,
                    font=(FONT_NAME, 12),
                    fg=SIDEBAR_TEXT,
                    bg=SIDEBAR_BG,
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)

                tk.Label(
                    row,
                    text=self.format_task_time(task),
                    font=(FONT_NAME, 10),
                    fg=MUTED_TEXT,
                    bg=SIDEBAR_BG,
                ).pack(side="right", padx=(8, 0))

    def update_task_scroll_area(self, event):
        self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all"))

    def resize_task_list(self, event):
        self.task_canvas.itemconfig(self.task_list_window, width=event.width)

    def scroll_task_list(self, event):
        self.task_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def draw_month_view(self):
        month_frame = tk.Frame(self.calendar_area, bg=BG)
        month_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        for column in range(7):
            month_frame.columnconfigure(column, weight=1, uniform="month")

        for row in range(7):
            month_frame.rowconfigure(row, weight=1)

        day_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for column, day_name in enumerate(day_names):
            tk.Label(
                month_frame,
                text=day_name,
                font=(FONT_NAME, 11, "bold"),
                fg=MUTED_TEXT,
                bg=BG,
            ).grid(row=0, column=column, sticky="ew", pady=(0, 8))

        tasks_by_date = {}
        for task in self.matching_tasks():
            if task.task_date not in tasks_by_date:
                tasks_by_date[task.task_date] = []
            tasks_by_date[task.task_date].append(task)

        month_dates = self.month_dates_calendar(self.current_date.year, self.current_date.month)

        for row, week in enumerate(month_dates, start=1):
            for column, shown_date in enumerate(week):
                if shown_date == self.today:
                    background = LIGHT_BLUE
                    foreground = TODAY_FG
                elif shown_date.month == self.current_date.month:
                    background = SURFACE
                    foreground = TEXT
                else:
                    background = BG
                    foreground = OUT_OF_MONTH_FG

                cell = tk.Frame(
                    month_frame,
                    bg=background,
                    highlightbackground=GRID_LINE,
                    highlightthickness=1,
                )
                cell.grid(row=row, column=column, sticky="nsew")
                cell.bind("<Button-1>", lambda event, selected=shown_date: self.choose_date(selected))

                tk.Label(
                    cell,
                    text=str(shown_date.day),
                    font=(FONT_NAME, 13, "bold"),
                    fg=foreground,
                    bg=background,
                ).pack(anchor="nw", padx=8, pady=6)

                day_tasks = tasks_by_date.get(shown_date, [])
                for task in day_tasks[:4]:
                    tk.Label(
                        cell,
                        text=task.title,
                        font=(FONT_NAME, 10, "bold"),
                        fg=self.priority_text(task.priority),
                        bg=self.priority_bg(task.priority),
                        anchor="w",
                        padx=6,
                    ).pack(fill="x", padx=6, pady=2)

    def priority_bg(self, priority):
        return PRIORITY_COLOURS.get(priority, PRIORITY_COLOURS["low"])["bg"]

    def priority_border(self, priority):
        return PRIORITY_COLOURS.get(priority, PRIORITY_COLOURS["low"])["border"]

    def priority_text(self, priority):
        return PRIORITY_COLOURS.get(priority, PRIORITY_COLOURS["low"])["text"]

    def format_task_time(self, task):
        if task.start_hour is None:
            return "all-day"

        hour = int(task.start_hour)
        minute = int(round((task.start_hour - hour) * 60))

        if hour < 12:
            suffix = "AM"
        else:
            suffix = "PM"

        display_hour = hour
        if display_hour > 12:
            display_hour = display_hour - 12
        if display_hour == 0:
            display_hour = 12

        return str(display_hour) + ":" + str(minute).zfill(2) + " " + suffix

    def last_day_of_month(self, year, month):
        if month == 12:
            first_day_next_month = date(year + 1, 1, 1)
        else:
            first_day_next_month = date(year, month + 1, 1)

        return (first_day_next_month - timedelta(days=1)).day

    def month_dates_calendar(self, year, month):
        first_day = date(year, month, 1)
        days_before_monday = first_day.weekday()
        grid_start = first_day - timedelta(days=days_before_monday)

        weeks = []
        current_day = grid_start

        for row in range(6):
            week = []
            for column in range(7):
                week.append(current_day)
                current_day = current_day + timedelta(days=1)
            weeks.append(week)

        if weeks[-1][0].month != month and weeks[-1][-1].month != month:
            weeks.pop()

        return weeks


if __name__ == "__main__":
    # Standalone preview — useful while iterating on the calendar's UI
    # without running the whole app. No controller, so the grid is empty.
    root = tk.Tk()
    root.title("Calendar")
    root.geometry("1280x760")
    root.configure(bg=BG)
    calendar = CalendarView(root, controller=None)
    calendar.pack(fill="both", expand=True)
    root.mainloop()
