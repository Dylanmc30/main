#!/usr/bin/env python3
"""Graphical todo list using tkinter."""

import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

TODO_FILE = Path.home() / ".todos.json"

BG = "#1e1e2e"
SURFACE = "#2a2a3d"
ACCENT = "#7c6af7"
ACCENT_HOVER = "#9d8fff"
TEXT = "#cdd6f4"
SUBTEXT = "#6c7086"
GREEN = "#a6e3a1"
RED = "#f38ba8"
FONT = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")


def load() -> list[dict]:
    if not TODO_FILE.exists():
        return []
    return json.loads(TODO_FILE.read_text())


def save(todos: list[dict]) -> None:
    TODO_FILE.write_text(json.dumps(todos, indent=2))


def next_id(todos: list[dict]) -> int:
    return (max(t["id"] for t in todos) + 1) if todos else 1


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Todo List")
        self.geometry("500x600")
        self.minsize(400, 400)
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build()
        self.refresh()

    def _build(self):
        # Title
        tk.Label(self, text="My Todo List", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(pady=(24, 4))
        tk.Label(self, text="stay on top of things", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 10)).pack(pady=(0, 16))

        # Input row
        input_frame = tk.Frame(self, bg=BG)
        input_frame.pack(fill="x", padx=24, pady=(0, 16))

        self.entry = tk.Entry(input_frame, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                              font=FONT, relief="flat", bd=0)
        self.entry.pack(side="left", fill="x", expand=True, ipady=10, ipadx=10)
        self.entry.bind("<Return>", lambda e: self.add_task())

        add_btn = tk.Button(input_frame, text="Add", bg=ACCENT, fg="white",
                            font=FONT_BOLD, relief="flat", bd=0, cursor="hand2",
                            activebackground=ACCENT_HOVER, activeforeground="white",
                            command=self.add_task)
        add_btn.pack(side="left", padx=(8, 0), ipadx=16, ipady=10)

        # Filter tabs
        tab_frame = tk.Frame(self, bg=BG)
        tab_frame.pack(fill="x", padx=24, pady=(0, 8))

        self.filter = tk.StringVar(value="pending")
        for label, value in [("Pending", "pending"), ("All", "all"), ("Done", "done")]:
            tk.Radiobutton(tab_frame, text=label, variable=self.filter, value=value,
                           bg=BG, fg=SUBTEXT, selectcolor=BG, activebackground=BG,
                           activeforeground=TEXT, font=FONT, indicatoron=False,
                           relief="flat", bd=0, cursor="hand2",
                           command=self.refresh).pack(side="left", padx=(0, 8), ipadx=10, ipady=4)

        # Task list canvas (scrollable)
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.task_frame = tk.Frame(self.canvas, bg=BG)

        self.task_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.task_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # Footer
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=24, pady=(0, 16))

        self.status_label = tk.Label(footer, text="", bg=BG, fg=SUBTEXT, font=("Segoe UI", 9))
        self.status_label.pack(side="left")

        tk.Button(footer, text="Clear completed", bg=SURFACE, fg=SUBTEXT,
                  font=("Segoe UI", 9), relief="flat", bd=0, cursor="hand2",
                  activebackground=BG, activeforeground=TEXT,
                  command=self.clear_done).pack(side="right")

    def refresh(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        todos = load()
        f = self.filter.get()
        if f == "pending":
            items = [t for t in todos if not t["done"]]
        elif f == "done":
            items = [t for t in todos if t["done"]]
        else:
            items = todos

        if not items:
            msg = "Nothing here yet — add a task above!" if f == "pending" else "Nothing to show."
            tk.Label(self.task_frame, text=msg, bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 10)).pack(pady=32)
        else:
            for t in items:
                self._task_row(t)

        done_count = sum(1 for t in todos if t["done"])
        self.status_label.config(text=f"{done_count}/{len(todos)} completed")

    def _task_row(self, task: dict):
        row = tk.Frame(self.task_frame, bg=SURFACE, pady=2)
        row.pack(fill="x", pady=4)

        var = tk.BooleanVar(value=task["done"])
        cb = tk.Checkbutton(row, variable=var, bg=SURFACE, activebackground=SURFACE,
                            selectcolor=SURFACE, cursor="hand2",
                            command=lambda tid=task["id"], v=var: self.toggle(tid, v))
        cb.pack(side="left", padx=(10, 4), pady=8)

        color = SUBTEXT if task["done"] else TEXT
        font = ("Segoe UI", 11, "overstrike") if task["done"] else FONT
        tk.Label(row, text=task["task"], bg=SURFACE, fg=color,
                 font=font, anchor="w").pack(side="left", fill="x", expand=True, pady=8)

        del_btn = tk.Button(row, text="✕", bg=SURFACE, fg=SUBTEXT, font=("Segoe UI", 10),
                            relief="flat", bd=0, cursor="hand2",
                            activebackground=SURFACE, activeforeground=RED,
                            command=lambda tid=task["id"]: self.delete(tid))
        del_btn.pack(side="right", padx=(4, 10), pady=8)

    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            return
        todos = load()
        todos.append({
            "id": next_id(todos),
            "task": text,
            "done": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        save(todos)
        self.entry.delete(0, tk.END)
        self.filter.set("pending")
        self.refresh()

    def toggle(self, tid: int, var: tk.BooleanVar):
        todos = load()
        for t in todos:
            if t["id"] == tid:
                t["done"] = var.get()
                break
        save(todos)
        self.refresh()

    def delete(self, tid: int):
        todos = load()
        remaining = [t for t in todos if t["id"] != tid]
        save(remaining)
        self.refresh()

    def clear_done(self):
        todos = load()
        done_count = sum(1 for t in todos if t["done"])
        if done_count == 0:
            messagebox.showinfo("Nothing to clear", "No completed tasks to remove.")
            return
        if messagebox.askyesno("Clear completed", f"Remove {done_count} completed task(s)?"):
            save([t for t in todos if not t["done"]])
            self.refresh()


if __name__ == "__main__":
    TodoApp().mainloop()
