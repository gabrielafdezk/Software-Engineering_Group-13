import tkinter as tk
from datetime import date, timedelta
from tkinter import font as tkfont
from tkinter import ttk


FONT_NAME = "Segoe UI"

BLUE = "#2DA7FF"
LIGHT_BLUE = "#DFF1FF"
SIDEBAR_BG = "#0C2C75"
SIDEBAR_TEXT = "#F4F7FF"
MUTED_TEXT = "#AAB7D8"
GRID_LINE = "#DDDDDD"

PRIORITY_COLOURS = {
    "high": {
        "bg": "#F8D6D2",
        "border": "#E53935",
        "text": "#7F1D1D",
    },
    "medium": {
        "bg": "#FFF0C8",
        "border": "#F4B400",
        "text": "#7A5300",
    },
    "low": {
        "bg": "#D9F2D0",
        "border": "#4ECB3F",
        "text": "#25651F",
    },
}


class CalendarTask:
    def __init__(self, title, task_date, start_hour, duration, priority):
        self.title = title
        self.task_date = task_date
        self.start_hour = start_hour
        self.duration = duration
        self.priority = priority


class CalendarWindow(tk.Toplevel):
    def __init__(self, master=None, home_command=None):
        tk.Toplevel.__init__(self, master)

        self.title("Calendar")
        self.geometry("1280x760")
        self.minsize(1050, 650)
        self.configure(bg="white")

        self.today = date.today()
        self.current_date = self.today
        self.home_command = home_command
        self.search_text = tk.StringVar()
        self.search_text.trace("w", self.refresh_from_search)

        self.tasks = self.make_example_tasks()

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
            background="#F7F7F7",
            foreground="#555555",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Nav.TButton",
            background=[("active", "#ECECEC"), ("pressed", "#E2E2E2")],
            foreground=[("active", "#222222")],
        )

        style.configure(
            "Today.TButton",
            font=(FONT_NAME, 11, "bold"),
            padding=(18, 7),
            background="#F7F7F7",
            foreground="#333333",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Today.TButton",
            background=[("active", "#ECECEC"), ("pressed", "#E2E2E2")],
            foreground=[("active", "#111111")],
        )

        style.configure("TButton", font=(FONT_NAME, 10))
        style.configure("TEntry", font=(FONT_NAME, 12))
        style.configure(
            "Minimal.Vertical.TScrollbar",
            gripcount=0,
            background="#B8B8B8",
            darkcolor="#B8B8B8",
            lightcolor="#B8B8B8",
            troughcolor="#F7F7F7",
            bordercolor="#F7F7F7",
            arrowcolor="#F7F7F7",
            relief="flat",
            borderwidth=0,
            width=10,
        )
        style.map(
            "Minimal.Vertical.TScrollbar",
            background=[("active", "#A6A6A6"), ("pressed", "#999999")],
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
            background=[("active", "#173B8E"), ("pressed", "#08235E")],
            foreground=[("active", "white")],
        )

    def create_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=310)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.main_area = tk.Frame(self, bg="white")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.rowconfigure(1, weight=1)

        self.create_sidebar()
        self.create_top_bar()

        self.calendar_area = tk.Frame(self.main_area, bg="white")
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
        self.draw_home_icon("#F4F7FF")
        self.home_button.bind("<Button-1>", lambda event: self.go_home())
        self.home_button.bind("<Enter>", lambda event: self.draw_home_icon("#FFFFFF"))
        self.home_button.bind("<Leave>", lambda event: self.draw_home_icon("#F4F7FF"))

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
        top_bar = tk.Frame(self.main_area, bg="#F7F7F7", height=72)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_propagate(False)
        top_bar.columnconfigure(1, weight=1)

        navigation = tk.Frame(top_bar, bg="#F7F7F7")
        navigation.grid(row=0, column=0, sticky="w", padx=14, pady=16)

        ttk.Button(navigation, text="<", style="Nav.TButton", command=lambda: self.change_month(-1)).pack(side="left")
        ttk.Button(navigation, text="Today", style="Today.TButton", command=self.go_to_today).pack(side="left", padx=1)
        ttk.Button(navigation, text=">", style="Nav.TButton", command=lambda: self.change_month(1)).pack(side="left")

        top_month_title = tk.Label(
            top_bar,
            text="Monthly Calendar",
            font=(FONT_NAME, 13, "bold"),
            fg="#333333",
            bg="#F7F7F7",
        )
        top_month_title.grid(row=0, column=1, pady=16)

        search_entry = tk.Entry(
            top_bar,
            textvariable=self.search_text,
            font=(FONT_NAME, 12),
            bg="#E6E6E6",
            fg="#333333",
            relief="flat",
            width=28,
            insertbackground="#333333",
        )
        search_entry.grid(row=0, column=2, sticky="e", padx=16, pady=16, ipady=8)
        search_entry.insert(0, "")

    def make_example_tasks(self):
        return []

    def refresh_from_search(self, name, index, mode):
        self.refresh()

    def refresh(self):
        self.month_title.config(text=self.current_date.strftime("%B %Y"))
        self.draw_sidebar_week_tasks()

        for widget in self.calendar_area.winfo_children():
            widget.destroy()

        self.draw_month_view()

    def go_to_today(self):
        self.current_date = self.today
        self.refresh()

    def go_home(self):
        if self.home_command is not None:
            self.home_command()
        else:
            self.destroy()

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
        month_frame = tk.Frame(self.calendar_area, bg="white")
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
                bg="white",
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
                elif shown_date.month == self.current_date.month:
                    background = "white"
                else:
                    background = "#F6F6F6"

                cell = tk.Frame(
                    month_frame,
                    bg=background,
                    highlightbackground=GRID_LINE,
                    highlightthickness=1,
                )
                cell.grid(row=row, column=column, sticky="nsew")
                cell.bind("<Button-1>", lambda event, selected=shown_date: self.choose_date(selected))

                foreground = "#222222" if shown_date.month == self.current_date.month else "#AAAAAA"

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


def open_calendar(master=None, home_command=None):
    return CalendarWindow(master, home_command)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    calendar_window = open_calendar(root)
    calendar_window.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
