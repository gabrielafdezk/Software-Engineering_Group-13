import os
import sys
import tkinter as tk

from views.main_menu import MainMenu
from controllers.app_controller import AppController
from views.sidebar import Sidebar
from views.splash import Splash
from views.timer import TimerView
from views.calendar_view import CalendarView
from views.task_form_view import TaskFormView


def _enable_dpi_awareness():
    """
    On Windows high-DPI displays, mark the process as DPI-aware so the OS
    doesn't bitmap-stretch the Tk window (which causes blur/graininess).
    Must be called before any Tk widget is created.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


WINDOW_TITLE = "Smart-Task — Academic Project Manager"
WINDOW_W = 1100
WINDOW_H = 700
MIN_W = 900
MIN_H = 600
CONTENT_BG = "#0f1419"
TEXT_FG = "#e2e8f0"
TEXT_MUTED = "#94a3b8"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "tasks.csv")


class PlaceholderScreen(tk.Frame):
    """Temporary screen shown while a teammate's view is still in progress."""

    def __init__(self, parent, title, owner):
        super().__init__(parent, bg=CONTENT_BG)
        tk.Label(
            self,
            text=title,
            bg=CONTENT_BG,
            fg=TEXT_FG,
            font=("Segoe UI", 24, "bold"),
        ).pack(pady=(48, 8))
        tk.Label(
            self,
            text=f"This screen is being built by {owner}.",
            bg=CONTENT_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 11),
        ).pack()


class App(tk.Tk):
    """
    Root window for Smart-Task.
    Hosts the sidebar on the left and a stack of screen frames on the right.
    Screens are stacked in the same grid cell and raised with tkraise().
    """

    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.scale = self.winfo_fpixels("1i") / 96
        self.geometry(
            f"{int(WINDOW_W * self.scale)}x{int(WINDOW_H * self.scale)}"
        )
        self.minsize(int(MIN_W * self.scale), int(MIN_H * self.scale))
        self.configure(bg=CONTENT_BG)

        self.controller = AppController(DATA_FILE)
        self.controller.show_frame = self.show_frame

        self.sidebar = Sidebar(self, on_select=self.show_screen)
        self.sidebar.pack(side="left", fill="y")

        self.container = tk.Frame(self, bg=CONTENT_BG)
        self.container.pack(side="left", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.screens = self._build_screens()
        self.show_screen("dashboard")

    def _build_screens(self):
        screens = {
            "dashboard": MainMenu(self.container, self.controller),

            "tasks": TaskFormView(self.container, self.controller),

            "calendar": CalendarView(
                self.container,
                home_command=lambda: self.show_screen("dashboard"),
                tasks=self.controller.get_all_tasks(),
            ),

            "add_task": TaskFormView(self.container, self.controller),

            "timer": TimerView(self.container),
        }

        for screen in screens.values():
            screen.grid(row=0, column=0, sticky="nsew")
        return screens

    def show_frame(self, name):
        screen_map = {
            "AddTask": "add_task",
            "TaskList": "tasks",
            "SearchFilter": "tasks",
            "DeadlineTracker": "calendar",
            "Timer": "timer",
        }

        key = screen_map.get(name, name)
        self.show_screen(key)


    def show_screen(self, key):
        if key not in self.screens:
            return

        screen = self.screens[key]

        if key == "dashboard" and hasattr(screen, "refresh"):
            screen.refresh()

        if key == "calendar" and hasattr(screen, "set_tasks"):
            screen.set_tasks(self.controller.get_all_tasks())

        if key in ["tasks", "add_task"] and hasattr(screen, "load_tasks"):
            screen.load_tasks()

        screen.tkraise()
        self.sidebar.set_active(key)



def main():
    _enable_dpi_awareness()
    app = App()
    app.withdraw()
    Splash(app, on_start=app.deiconify)
    app.mainloop()


if __name__ == "__main__":
    main()
