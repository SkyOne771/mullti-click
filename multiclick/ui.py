import queue
import tkinter as tk
from tkinter import ttk, messagebox

from .engine import ClickEngine
from .windows import WindowsBackend, send_click, user32


def run():
    root = tk.Tk()
    root.title("Multi Click")
    root.geometry("470x590")
    root.minsize(430, 570)
    root.configure(bg="#11151e")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TSpinbox", padding=8, font=("Segoe UI", 12))
    engine = ClickEngine(send_click)
    events = queue.SimpleQueue()
    root.update_idletasks()
    hwnd = user32.GetAncestor(root.winfo_id(), 2)
    backend = WindowsBackend(hwnd, events.put)
    multiplier = tk.StringVar(value="5")
    interval = tk.StringVar(value="40")

    frame = tk.Frame(root, bg="#11151e", padx=30, pady=25)
    frame.pack(fill="both", expand=True)

    def label(text, size=11, color="#a5afc2", **kwargs):
        widget = tk.Label(frame, text=text, bg="#11151e", fg=color,
                          font=("Segoe UI", size), **kwargs)
        widget.pack(anchor="w", pady=(0, 10))
        return widget

    label("M U L T I  C L I C K", 11, "#8d9eff")
    label("One click. More power.", 24, "#f1f4fc")
    label("Multiply your left clicks across Windows.")
    status = label("●  PAUSED", 12, "#a5afc2")
    label("CLICKS PER PHYSICAL CLICK", 10)
    presets = tk.Frame(frame, bg="#11151e")
    presets.pack(fill="x", pady=(0, 12))
    preset_buttons = {}

    def choose(value):
        multiplier.set(str(value))

    for value in (2, 5, 10, 20):
        button = tk.Button(presets, text=f"{value}×", command=lambda n=value: choose(n),
                           bg="#242c3e", fg="#edf1ff", activebackground="#4659b8",
                           activeforeground="white", relief="flat", font=("Segoe UI", 13),
                           padx=16, pady=9, cursor="hand2")
        button.pack(side="left", expand=True, fill="x", padx=(0, 6))
        preset_buttons[value] = button

    fields = tk.Frame(frame, bg="#11151e")
    fields.pack(fill="x", pady=(0, 14))
    for title, variable, low, high in [
        ("Custom multiplier (2–100)", multiplier, 2, 100),
        ("Click interval (ms)", interval, 10, 1000),
    ]:
        column = tk.Frame(fields, bg="#11151e")
        column.pack(side="left", expand=True, fill="x", padx=(0, 10))
        tk.Label(column, text=title, bg="#11151e", fg="#a5afc2",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 6))
        ttk.Spinbox(column, from_=low, to=high, textvariable=variable, width=13).pack(fill="x")

    description = label("", 11, "#d8dff0")
    validation = label("", 10, "#ffbba5", wraplength=390)

    def validate(*_):
        try:
            engine.configure(int(multiplier.get()), int(interval.get()))
        except (ValueError, tk.TclError) as exc:
            engine.set_enabled(False)
            validation.config(text=str(exc) if "invalid literal" not in str(exc) else "Enter whole numbers for both settings.")
            return False
        validation.config(text="")
        description.config(text=f"1 physical click → {multiplier.get()} total clicks")
        for value, button in preset_buttons.items():
            button.config(bg="#485ec9" if str(value) == multiplier.get() else "#242c3e")
        return True

    def toggle():
        enabled, _, _, error = engine.snapshot()
        if error or backend.error:
            engine.set_enabled(False)
        elif enabled:
            engine.set_enabled(False)
        elif validate():
            engine.set_enabled(True)
        refresh()

    start = tk.Button(frame, text="Enable multiplier    F6", command=toggle,
                      bg="#8295ff", fg="#101629", activebackground="#a5b2ff",
                      relief="flat", font=("Segoe UI", 12, "bold"), pady=13, cursor="hand2")
    start.pack(fill="x", pady=(0, 12))
    label("F6  Toggle on / off       F8  Emergency stop", 10)
    counts = label("", 10)
    label("Extra clicks follow your cursor after you release the button.\nClicks inside this window are excluded.",
          10, wraplength=390, justify="left")

    def refresh():
        enabled, physical, extra, error = engine.snapshot()
        status.config(text="●  ACTIVE" if enabled else "●  PAUSED", fg="#8de6b0" if enabled else "#a5afc2")
        start.config(text="Pause multiplier    F6" if enabled else "Enable multiplier    F6")
        counts.config(text=f"Session: {physical:,} physical clicks  ·  {extra:,} extra clicks")
        if error or backend.error:
            validation.config(text=error or backend.error)
            start.config(state="disabled")

    def poll():
        while not events.empty():
            event = events.get()
            if event == "toggle":
                toggle()
            elif event == "stop":
                engine.set_enabled(False)
            elif event == "click":
                engine.physical_click()
        refresh()
        root.after(15, poll)

    def close():
        engine.set_enabled(False)
        backend.close()
        engine.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    multiplier.trace_add("write", validate)
    interval.trace_add("write", validate)
    validate()
    try:
        backend.start()
    except RuntimeError as exc:
        messagebox.showerror("Multi Click could not start", str(exc), parent=root)
        close()
        return
    poll()
    root.mainloop()
