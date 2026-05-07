import random
import sys
import time
import tkinter as tk


class Splash(tk.Toplevel):
    """
    Cosmic splash shown on app launch. Pure Tkinter — vertical gradient,
    sprinkled stars, two distant planets, and a planet-horizon arc, all drawn
    on a single Canvas. Auto-dismisses after a short cinematic moment; click
    anywhere or press Escape to skip.
    """

    BG_TOP = "#0a0d1a"
    BG_BOTTOM = "#1a0e2e"
    HORIZON_FILL = "#1a0e2e"
    HORIZON_OUTLINE = "#3d2a5e"
    LOGO_FG = "#c8b3ff"
    TEXT_FG = "#ffffff"
    TEXT_MUTED = "#9ca3c4"
    PROGRESS_BG = "#2a1f4a"
    PROGRESS_FG = "#a78bfa"
    PLANET_LG_FILL = "#4c2a7a"
    PLANET_LG_OUTLINE = "#7c4dca"
    PLANET_SM_FILL = "#3b2160"

    WIDTH = 600
    HEIGHT = 400
    DURATION_MS = 2800
    PROGRESS_TICK_MS = 30
    STAR_RNG_SEED = 7

    def __init__(self, parent, on_start):
        super().__init__(parent)
        self.on_start = on_start

        self.overrideredirect(True)
        self.configure(bg=self.BG_TOP)

        self.scale = self.winfo_fpixels("1i") / 96
        self._splash_w = int(self.WIDTH * self.scale)
        self._splash_h = int(self.HEIGHT * self.scale)

        self._dismissed = False
        self._start_time = time.time()
        self._dismiss_job = None

        self._center()
        self._build_canvas()

        self.protocol("WM_DELETE_WINDOW", self._dismiss)
        self.bind("<Button-1>", lambda _e: self._dismiss())
        self.bind("<Escape>", lambda _e: self._dismiss())
        self.canvas.bind("<Button-1>", lambda _e: self._dismiss())
        self.bind("<Destroy>", self._on_destroy)

        self.lift()
        self.focus_force()
        self.after_idle(self._center)

        self._dismiss_job = self.after(self.DURATION_MS, self._dismiss)
        self._animate_progress()

    def _center(self):
        self.update_idletasks()
        left, top, width, height = self._target_monitor_rect()
        x = left + (width - self._splash_w) // 2
        y = top + (height - self._splash_h) // 2
        self.geometry(f"{self._splash_w}x{self._splash_h}+{x}+{y}")

    def _target_monitor_rect(self):
        """
        Return (left, top, width, height) of the work area of the monitor
        containing the cursor — so the splash lands on whichever screen the
        user is actively looking at, excluding the taskbar. Falls back to
        Tk's primary-screen dims if the Win32 query fails or we're not on
        Windows.
        """
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                user32 = ctypes.windll.user32

                pt = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(pt))

                MONITOR_DEFAULTTONEAREST = 2
                hmon = user32.MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST)

                class MONITORINFO(ctypes.Structure):
                    _fields_ = [
                        ("cbSize", wintypes.DWORD),
                        ("rcMonitor", wintypes.RECT),
                        ("rcWork", wintypes.RECT),
                        ("dwFlags", wintypes.DWORD),
                    ]

                mi = MONITORINFO()
                mi.cbSize = ctypes.sizeof(MONITORINFO)
                if user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
                    rc = mi.rcWork
                    return (
                        rc.left,
                        rc.top,
                        rc.right - rc.left,
                        rc.bottom - rc.top,
                    )
            except Exception:
                pass
        return (0, 0, self.winfo_screenwidth(), self.winfo_screenheight())

    def _build_canvas(self):
        w, h = self._splash_w, self._splash_h
        self.canvas = tk.Canvas(
            self,
            width=w,
            height=h,
            bg=self.BG_TOP,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._draw_gradient(w, h)
        self._draw_stars(w, h)
        self._draw_planets(w, h)
        self._draw_horizon(w, h)
        self._draw_content(w, h)
        self._init_progress(w, h)

    def _draw_gradient(self, w, h):
        r1, g1, b1 = 0x0a, 0x0d, 0x1a
        r2, g2, b2 = 0x1a, 0x0e, 0x2e
        for i in range(h):
            t = i / max(1, h - 1)
            r = int((1 - t) * r1 + t * r2)
            g = int((1 - t) * g1 + t * g2)
            b = int((1 - t) * b1 + t * b2)
            self.canvas.create_line(
                0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}"
            )

    def _draw_stars(self, w, h):
        rng = random.Random(self.STAR_RNG_SEED)
        n_stars = max(180, w * h // 2200)
        upper_bound = int(h * 0.78)
        for _ in range(n_stars):
            x = rng.randint(0, w)
            y = rng.randint(0, upper_bound)
            roll = rng.random()
            if roll < 0.72:
                size = max(1, int(1 * self.scale))
                brightness = rng.randint(110, 200)
            elif roll < 0.94:
                size = max(1, int(2 * self.scale))
                brightness = rng.randint(180, 240)
            else:
                size = max(2, int(3 * self.scale))
                brightness = rng.randint(220, 255)
            tint = min(255, brightness + 10)
            color = f"#{brightness:02x}{brightness:02x}{tint:02x}"
            self.canvas.create_oval(
                x, y, x + size, y + size, fill=color, outline=""
            )

    def _draw_planets(self, w, h):
        cx = int(w * 0.84)
        cy = int(h * 0.18)
        r = int(36 * self.scale)
        self.canvas.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            fill=self.PLANET_LG_FILL,
            outline=self.PLANET_LG_OUTLINE,
            width=max(1, int(1.5 * self.scale)),
        )

        cx2 = int(w * 0.13)
        cy2 = int(h * 0.32)
        r2 = int(13 * self.scale)
        self.canvas.create_oval(
            cx2 - r2,
            cy2 - r2,
            cx2 + r2,
            cy2 + r2,
            fill=self.PLANET_SM_FILL,
            outline="",
        )

    def _draw_horizon(self, w, h):
        radius = int(w * 1.5)
        cx = w // 2
        cy = h + int(radius * 0.85)
        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=self.HORIZON_FILL,
            outline=self.HORIZON_OUTLINE,
            width=max(1, int(2 * self.scale)),
        )

    def _draw_content(self, w, h):
        cx = w // 2
        self.canvas.create_text(
            cx,
            int(h * 0.30),
            text="⬡",
            fill=self.LOGO_FG,
            font=("Segoe UI", 46, "bold"),
        )
        self.canvas.create_text(
            cx,
            int(h * 0.50),
            text="Smart-Task",
            fill=self.TEXT_FG,
            font=("Segoe UI", 26, "bold"),
        )
        self.canvas.create_text(
            cx,
            int(h * 0.60),
            text="Academic Project Manager",
            fill=self.TEXT_MUTED,
            font=("Segoe UI", 11),
        )

    def _init_progress(self, w, h):
        bar_w = int(w * 0.40)
        bar_h = max(2, int(3 * self.scale))
        x0 = (w - bar_w) // 2
        y0 = int(h * 0.78)
        self.canvas.create_rectangle(
            x0,
            y0,
            x0 + bar_w,
            y0 + bar_h,
            fill=self.PROGRESS_BG,
            outline="",
        )
        self.progress_bar = self.canvas.create_rectangle(
            x0,
            y0,
            x0,
            y0 + bar_h,
            fill=self.PROGRESS_FG,
            outline="",
        )
        self._progress_x0 = x0
        self._progress_y0 = y0
        self._progress_w = bar_w
        self._progress_h = bar_h
        self.canvas.create_text(
            w // 2,
            y0 + bar_h + int(18 * self.scale),
            text="Launching your productivity…",
            fill=self.TEXT_MUTED,
            font=("Segoe UI", 9),
        )

    def _animate_progress(self):
        if self._dismissed:
            return
        elapsed = (time.time() - self._start_time) * 1000
        progress = min(1.0, elapsed / self.DURATION_MS)
        filled = int(self._progress_w * progress)
        self.canvas.coords(
            self.progress_bar,
            self._progress_x0,
            self._progress_y0,
            self._progress_x0 + filled,
            self._progress_y0 + self._progress_h,
        )
        if progress < 1.0:
            self.after(self.PROGRESS_TICK_MS, self._animate_progress)

    def _dismiss(self):
        if self._dismissed:
            return
        self._dismissed = True
        if self._dismiss_job is not None:
            try:
                self.after_cancel(self._dismiss_job)
            except tk.TclError:
                pass
        try:
            self.on_start()
        finally:
            self.destroy()

    def _on_destroy(self, event):
        if event.widget is not self or self._dismissed:
            return
        self._dismissed = True
        try:
            self.on_start()
        except Exception:
            pass
