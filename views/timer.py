import math
import time
import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageDraw, ImageTk
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False


class TimerView(tk.Frame):
    """
    Pomodoro timer screen, Pulse styling.
    Circular progress ring drawn on a Canvas, drains as time elapses.
    Phases: Work -> Short Break, repeating. Every Nth break is a Long Break,
    where N is configurable via the Settings dialog.
    """

    BG = "#0f1419"
    SURFACE = "#1a1f2e"
    TEXT = "#e2e8f0"
    TEXT_MUTED = "#94a3b8"

    PHASE_LABELS = {
        "work": "FOCUS",
        "short_break": "SHORT BREAK",
        "long_break": "LONG BREAK",
    }
    PHASE_COLOURS = {
        "work": "#a855f7",
        "short_break": "#10b981",
        "long_break": "#3b82f6",
    }
    PHASE_DIM = {
        "work": "#3d2952",
        "short_break": "#1e3a32",
        "long_break": "#1e2a4a",
    }
    DEFAULT_DURATIONS = {
        "work": 25 * 60,
        "short_break": 5 * 60,
        "long_break": 15 * 60,
    }
    DEFAULT_POMODOROS_BEFORE_LONG = 4

    PRIMARY_BG = "#3b82f6"
    SECONDARY_BG = "#252b3d"

    RING_SIZE = 320
    RING_THICKNESS = 14
    RING_PADDING = 24

    def __init__(self, parent):
        super().__init__(parent, bg=self.BG)

        self.scale = self.winfo_fpixels("1i") / 96
        self._ring_size = int(self.RING_SIZE * self.scale)
        self._ring_thickness = max(1, int(self.RING_THICKNESS * self.scale))
        self._ring_padding = int(self.RING_PADDING * self.scale)

        self.durations = dict(self.DEFAULT_DURATIONS)
        self.pomodoros_before_long = self.DEFAULT_POMODOROS_BEFORE_LONG

        self.phase = "work"
        self.pomodoros_done = 0
        self.remaining = self.durations[self.phase]
        self.end_time = None
        self.running = False
        self._tick_job = None

        self._build_ui()
        self._update_display()

    def _build_ui(self):
        tk.Frame(self, bg=self.BG, height=20).pack()

        size = self._ring_size
        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            bg=self.BG,
            highlightthickness=0,
        )
        self.canvas.pack(pady=(20, 8))

        if _HAS_PILLOW:
            self._ring_photo = self._render_ring(1.0)
            self.ring_item = self.canvas.create_image(
                size // 2, size // 2, image=self._ring_photo
            )
            self.bg_arc = None
            self.fg_arc = None
        else:
            bbox = (
                self._ring_padding,
                self._ring_padding,
                size - self._ring_padding,
                size - self._ring_padding,
            )
            self.bg_arc = self.canvas.create_arc(
                *bbox,
                start=0,
                extent=359.99,
                style="arc",
                outline=self.PHASE_DIM[self.phase],
                width=self._ring_thickness,
            )
            self.fg_arc = self.canvas.create_arc(
                *bbox,
                start=90,
                extent=-359.99,
                style="arc",
                outline=self.PHASE_COLOURS[self.phase],
                width=self._ring_thickness,
            )
            self.ring_item = None
            self._ring_photo = None

        cx = size // 2
        self.time_text = self.canvas.create_text(
            cx, cx - int(14 * self.scale),
            text="25:00",
            fill=self.TEXT,
            font=("Consolas", 56, "bold"),
        )
        self.phase_text = self.canvas.create_text(
            cx, cx + int(32 * self.scale),
            text="FOCUS",
            fill=self.PHASE_COLOURS[self.phase],
            font=("Segoe UI", 11, "bold"),
        )

        self.session_label = tk.Label(
            self,
            text="",
            bg=self.BG,
            fg=self.TEXT_MUTED,
            font=("Segoe UI", 11),
        )
        self.session_label.pack(pady=(4, 0))

        controls = tk.Frame(self, bg=self.BG)
        controls.pack(pady=24)

        self.start_button = self._make_button(
            controls, "Start", self._toggle, self.PRIMARY_BG, "white"
        )
        self.start_button.pack(side="left", padx=6)

        self._make_button(
            controls, "Reset", self._reset, self.SECONDARY_BG, self.TEXT
        ).pack(side="left", padx=6)

        self._make_button(
            controls, "Skip", self._skip, self.SECONDARY_BG, self.TEXT
        ).pack(side="left", padx=6)

        self._make_button(
            controls, "Settings", self._open_settings, self.SECONDARY_BG, self.TEXT
        ).pack(side="left", padx=6)

    def _make_button(self, parent, text, command, bg, fg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            bd=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=22,
            pady=10,
        )

    def _update_display(self):
        minutes, seconds = divmod(self.remaining, 60)
        self.canvas.itemconfig(self.time_text, text=f"{minutes:02d}:{seconds:02d}")
        self.canvas.itemconfig(
            self.phase_text,
            text=self.PHASE_LABELS[self.phase],
            fill=self.PHASE_COLOURS[self.phase],
        )

        total = self.durations[self.phase]
        progress = self.remaining / total if total > 0 else 0

        if _HAS_PILLOW:
            self._ring_photo = self._render_ring(progress)
            self.canvas.itemconfig(self.ring_item, image=self._ring_photo)
        else:
            extent = -360 * progress
            if extent == 0:
                extent = -0.001
            self.canvas.itemconfig(
                self.bg_arc, outline=self.PHASE_DIM[self.phase]
            )
            self.canvas.itemconfig(
                self.fg_arc,
                outline=self.PHASE_COLOURS[self.phase],
                extent=extent,
            )

        self.session_label.configure(
            text=f"Pomodoros completed: {self.pomodoros_done}"
        )
        self.start_button.configure(text="Pause" if self.running else "Start")

    def _toggle(self):
        if self.running:
            self._pause()
        else:
            self._start()

    def _start(self):
        if self.remaining <= 0:
            self.remaining = self.durations[self.phase]
        self.end_time = time.time() + self.remaining
        self.running = True
        self._update_display()
        self._tick()

    def _pause(self):
        self.running = False
        self._cancel_tick()
        self._update_display()

    def _tick(self):
        if not self.running:
            return
        self.remaining = max(0, math.ceil(self.end_time - time.time()))
        self._update_display()
        if self.remaining <= 0:
            self._complete_phase()
        else:
            self._tick_job = self.after(1000, self._tick)

    def _cancel_tick(self):
        if self._tick_job is not None:
            self.after_cancel(self._tick_job)
            self._tick_job = None

    def _complete_phase(self):
        self.running = False
        self._cancel_tick()
        try:
            self.bell()
        except tk.TclError:
            pass

        finished = self.PHASE_LABELS[self.phase]
        self._advance_phase()
        self._update_display()

        upcoming = self.PHASE_LABELS[self.phase]
        messagebox.showinfo(
            "Pomodoro Timer",
            f"{finished} finished. Up next: {upcoming}.",
        )

    def _advance_phase(self):
        if self.phase == "work":
            self.pomodoros_done += 1
            if self.pomodoros_done % self.pomodoros_before_long == 0:
                self.phase = "long_break"
            else:
                self.phase = "short_break"
        else:
            self.phase = "work"

        self.remaining = self.durations[self.phase]
        self.end_time = None

    def _reset(self):
        self.running = False
        self._cancel_tick()
        self.remaining = self.durations[self.phase]
        self.end_time = None
        self._update_display()

    def _skip(self):
        self.running = False
        self._cancel_tick()
        self._advance_phase()
        self._update_display()

    def _open_settings(self):
        SettingsDialog(self)

    def _render_ring(self, progress):
        """
        Render the progress ring as an anti-aliased PhotoImage. Drawn at 4x
        target size in Pillow, then downsampled with LANCZOS for smooth edges.
        """
        size = self._ring_size
        thickness = self._ring_thickness
        factor = 4
        big = size * factor
        big_t = thickness * factor
        pad = big_t // 2

        img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = (pad, pad, big - pad, big - pad)

        draw.ellipse(
            bbox,
            outline=self.PHASE_DIM[self.phase],
            width=big_t,
        )

        if progress > 0:
            start = 270.0
            sweep = 360.0 * progress
            if sweep >= 359.99:
                sweep = 359.99
            draw.arc(
                bbox,
                start=start,
                end=start + sweep,
                fill=self.PHASE_COLOURS[self.phase],
                width=big_t,
            )

        img = img.resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def apply_settings(self, durations, pomodoros_before_long):
        """
        Update timer settings. Durations is {phase: seconds}.
        New durations take effect on the next reset, skip, or phase completion;
        if the timer isn't running, the current display refreshes too.
        """
        self.durations = dict(durations)
        self.pomodoros_before_long = pomodoros_before_long
        if not self.running:
            self.remaining = self.durations[self.phase]
            self._update_display()


class SettingsDialog(tk.Toplevel):
    """Modal dialog for adjusting timer durations and the long-break cycle."""

    BG = "#1a1f2e"
    INPUT_BG = "#0f1419"
    FG = "#e2e8f0"
    FG_MUTED = "#94a3b8"
    PRIMARY_BG = "#3b82f6"
    SECONDARY_BG = "#252b3d"

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner

        self.title("Timer Settings")
        self.configure(bg=self.BG)
        self.resizable(False, False)
        self.transient(owner.winfo_toplevel())
        self.grab_set()

        self.work_var = tk.IntVar(value=owner.durations["work"] // 60)
        self.short_var = tk.IntVar(value=owner.durations["short_break"] // 60)
        self.long_var = tk.IntVar(value=owner.durations["long_break"] // 60)
        self.cycle_var = tk.IntVar(value=owner.pomodoros_before_long)

        self._build_ui()
        self._center_on_parent()

    def _build_ui(self):
        tk.Frame(self, bg=self.BG, height=8).pack()

        self._add_row("Work (minutes):", self.work_var, 1, 180)
        self._add_row("Short break (minutes):", self.short_var, 1, 60)
        self._add_row("Long break (minutes):", self.long_var, 1, 180)
        self._add_row("Long break every N pomodoros:", self.cycle_var, 1, 12)

        button_row = tk.Frame(self, bg=self.BG)
        button_row.pack(fill="x", padx=20, pady=(8, 16))

        self._make_button(
            button_row, "Cancel", self.destroy, self.SECONDARY_BG, self.FG
        ).pack(side="right", padx=(8, 0))

        self._make_button(
            button_row, "Save", self._save, self.PRIMARY_BG, "white"
        ).pack(side="right")

    def _add_row(self, label, var, from_, to):
        row = tk.Frame(self, bg=self.BG)
        row.pack(fill="x", padx=20, pady=8)

        tk.Label(
            row,
            text=label,
            bg=self.BG,
            fg=self.FG,
            font=("Segoe UI", 11),
        ).pack(side="left")

        tk.Spinbox(
            row,
            from_=from_,
            to=to,
            textvariable=var,
            width=6,
            font=("Segoe UI", 11),
            bg=self.INPUT_BG,
            fg=self.FG,
            buttonbackground=self.SECONDARY_BG,
            insertbackground=self.FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.SECONDARY_BG,
            highlightcolor=self.PRIMARY_BG,
        ).pack(side="right")

    def _make_button(self, parent, text, command, bg, fg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            bd=0,
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            padx=20,
            pady=8,
        )

    def _center_on_parent(self):
        self.update_idletasks()
        parent = self.master
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _save(self):
        try:
            work = int(self.work_var.get())
            short = int(self.short_var.get())
            long_ = int(self.long_var.get())
            cycle = int(self.cycle_var.get())
        except (ValueError, tk.TclError):
            messagebox.showerror(
                "Invalid input",
                "Please enter whole numbers.",
                parent=self,
            )
            return

        if min(work, short, long_, cycle) < 1:
            messagebox.showerror(
                "Invalid input",
                "All values must be at least 1.",
                parent=self,
            )
            return

        self.owner.apply_settings(
            durations={
                "work": work * 60,
                "short_break": short * 60,
                "long_break": long_ * 60,
            },
            pomodoros_before_long=cycle,
        )
        self.destroy()
