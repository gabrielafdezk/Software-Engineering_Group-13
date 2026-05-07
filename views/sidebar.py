import random
import tkinter as tk


class Sidebar(tk.Frame):
    """
    Astral sidebar — dark navy bg, sparkle logo, glyph-icon nav items, with
    a cosmic illustration (gradient + stars + planet horizon) at the bottom
    that visually rhymes with the splash screen.

    A chevron in the top-right corner toggles between expanded and collapsed.
    Calls on_select(screen_key) when a nav item is clicked. The parent is
    responsible for switching screens and then calling set_active(key).
    """

    BG = "#0a0d1a"
    BG_HOVER = "#1a1f3a"
    BG_ACTIVE = "#7c3aed"
    FG = "#94a3b8"
    FG_HOVER = "#cbd5e1"
    FG_ACTIVE = "#ffffff"
    HEADER_FG = "#ffffff"
    SUBTITLE_FG = "#9ca3c4"
    LOGO_BG = "#2a1f4a"
    LOGO_FG = "#c8b3ff"
    DIVIDER = "#1f1640"

    GRADIENT_TOP = (0x0a, 0x0d, 0x1a)
    GRADIENT_BOTTOM = (0x1a, 0x0e, 0x2e)
    PLANET_FILL = "#1a0e3a"
    PLANET_OUTLINE = "#7c4dca"

    WIDTH_EXPANDED = 240
    WIDTH_COLLAPSED = 60
    BADGE_SIZE = 60
    COSMIC_HEIGHT = 160
    COSMIC_RNG_SEED = 11

    SCREENS = [
        ("dashboard", "Dashboard", "⌂"),
        ("tasks", "Tasks", "☑"),
        ("calendar", "Calendar", "▦"),
        ("add_task", "Add Task", "+"),
        ("timer", "Timer", "◷"),
    ]

    def __init__(self, parent, on_select):
        scale = parent.winfo_fpixels("1i") / 96
        self.scale = scale
        self._width_expanded = int(self.WIDTH_EXPANDED * scale)
        self._width_collapsed = int(self.WIDTH_COLLAPSED * scale)
        self._badge_size = int(self.BADGE_SIZE * scale)
        self._cosmic_height = int(self.COSMIC_HEIGHT * scale)

        super().__init__(parent, bg=self.BG, width=self._width_expanded)
        self.pack_propagate(False)

        self.on_select = on_select
        self.buttons = {}
        self.active_key = None
        self.collapsed = False

        self._build_chevron()
        self._build_cosmic_footer()
        self._build_content()

    def _build_chevron(self):
        bar = tk.Frame(self, bg=self.BG)
        bar.pack(fill="x")

        self.chevron = tk.Button(
            bar,
            text="‹",
            command=self.toggle,
            bg=self.BG,
            fg=self.FG,
            activebackground=self.BG_HOVER,
            activeforeground=self.FG_HOVER,
            bd=0,
            relief="flat",
            font=("Segoe UI", 16, "bold"),
            cursor="hand2",
            padx=10,
            pady=4,
        )
        self.chevron.pack(side="right", padx=6, pady=4)
        self.chevron.bind(
            "<Enter>",
            lambda _e: self.chevron.configure(bg=self.BG_HOVER, fg=self.FG_HOVER),
        )
        self.chevron.bind(
            "<Leave>",
            lambda _e: self.chevron.configure(bg=self.BG, fg=self.FG),
        )

    def _build_cosmic_footer(self):
        self.cosmic_canvas = tk.Canvas(
            self,
            height=self._cosmic_height,
            bg=self.BG,
            highlightthickness=0,
            bd=0,
        )
        self.cosmic_canvas.pack(side="bottom", fill="x")
        self.cosmic_canvas.bind("<Configure>", self._draw_cosmic)

    def _draw_cosmic(self, event=None):
        canvas = self.cosmic_canvas
        canvas.delete("all")
        if event is not None:
            w, h = event.width, event.height
        else:
            w = canvas.winfo_width()
            h = canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        r1, g1, b1 = self.GRADIENT_TOP
        r2, g2, b2 = self.GRADIENT_BOTTOM
        for i in range(h):
            t = i / max(1, h - 1)
            r = int((1 - t) * r1 + t * r2)
            g = int((1 - t) * g1 + t * g2)
            b = int((1 - t) * b1 + t * b2)
            canvas.create_line(0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}")

        rng = random.Random(self.COSMIC_RNG_SEED)
        n = max(20, w * h // 600)
        upper = int(h * 0.55)
        for _ in range(n):
            x = rng.randint(0, w)
            y = rng.randint(0, upper)
            roll = rng.random()
            if roll < 0.78:
                size = max(1, int(1 * self.scale))
                brightness = rng.randint(140, 200)
            else:
                size = max(1, int(2 * self.scale))
                brightness = rng.randint(200, 240)
            tint = min(255, brightness + 15)
            color = f"#{brightness:02x}{brightness:02x}{tint:02x}"
            canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")

        radius = int(w * 1.3)
        cx = w // 2
        cy = h + int(radius * 0.82)
        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=self.PLANET_FILL,
            outline=self.PLANET_OUTLINE,
            width=max(1, int(1.5 * self.scale)),
        )

    def _build_content(self):
        self.content = tk.Frame(self, bg=self.BG)
        self.content.pack(fill="both", expand=True)

        badge = tk.Canvas(
            self.content,
            width=self._badge_size,
            height=self._badge_size,
            bg=self.BG,
            highlightthickness=0,
            bd=0,
        )
        badge.pack(pady=(4, 8))
        pad = max(2, int(3 * self.scale))
        badge.create_oval(
            pad,
            pad,
            self._badge_size - pad,
            self._badge_size - pad,
            fill=self.LOGO_BG,
            outline="",
        )
        badge.create_text(
            self._badge_size // 2,
            self._badge_size // 2,
            text="✦",
            fill=self.LOGO_FG,
            font=("Segoe UI", 22, "bold"),
        )

        tk.Label(
            self.content,
            text="Smart-Task",
            bg=self.BG,
            fg=self.HEADER_FG,
            font=("Segoe UI", 13, "bold"),
        ).pack(fill="x")

        tk.Label(
            self.content,
            text="Academic Project Manager",
            bg=self.BG,
            fg=self.SUBTITLE_FG,
            font=("Segoe UI", 9),
        ).pack(fill="x", pady=(2, 14))

        tk.Frame(self.content, bg=self.DIVIDER, height=1).pack(
            fill="x", pady=(0, 8), padx=16
        )

        for key, label, icon in self.SCREENS:
            btn = tk.Button(
                self.content,
                text=f"   {icon}    {label}",
                bg=self.BG,
                fg=self.FG,
                activebackground=self.BG_HOVER,
                activeforeground=self.FG_ACTIVE,
                bd=0,
                relief="flat",
                anchor="w",
                padx=14,
                pady=11,
                font=("Segoe UI", 11),
                cursor="hand2",
                command=lambda k=key: self.on_select(k),
            )
            btn.pack(fill="x", padx=10, pady=2)
            btn.bind("<Enter>", lambda _e, b=btn, k=key: self._on_hover(b, k, True))
            btn.bind("<Leave>", lambda _e, b=btn, k=key: self._on_hover(b, k, False))
            self.buttons[key] = btn

    def _on_hover(self, button, key, hovering):
        if key == self.active_key:
            return
        if hovering:
            button.configure(bg=self.BG_HOVER, fg=self.FG_HOVER)
        else:
            button.configure(bg=self.BG, fg=self.FG)

    def toggle(self):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.configure(width=self._width_collapsed)
            self.content.pack_forget()
            self.cosmic_canvas.pack_forget()
            self.chevron.configure(text="›")
        else:
            self.configure(width=self._width_expanded)
            self.cosmic_canvas.pack(side="bottom", fill="x")
            self.content.pack(fill="both", expand=True)
            self.chevron.configure(text="‹")

    def set_active(self, key):
        if key not in self.buttons:
            return
        if self.active_key and self.active_key in self.buttons:
            self.buttons[self.active_key].configure(bg=self.BG, fg=self.FG)
        self.buttons[key].configure(bg=self.BG_ACTIVE, fg=self.FG_ACTIVE)
        self.active_key = key
