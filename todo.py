#!/usr/bin/env python3
"""Interactive CLI todo list stored in a JSON file."""

import json
from datetime import datetime
from pathlib import Path

TODO_FILE = Path.home() / ".todos.json"


def load() -> list[dict]:
    if not TODO_FILE.exists():
        return []
    return json.loads(TODO_FILE.read_text())


def save(todos: list[dict]) -> None:
    TODO_FILE.write_text(json.dumps(todos, indent=2))


def next_id(todos: list[dict]) -> int:
    return (max(t["id"] for t in todos) + 1) if todos else 1


def show(todos: list[dict], show_all: bool = False) -> None:
    items = todos if show_all else [t for t in todos if not t["done"]]
    if not items:
        print("  (no tasks)" if show_all else "  (nothing pending)")
        return
    for t in items:
        status = "x" if t["done"] else " "
        print(f"  [{status}] {t['id']:>3}.  {t['task']}")


def main() -> None:
    print("=== Todo List ===")
    print("Type 'help' to see commands.\n")

    while True:
        todos = load()
        show(todos)

        try:
            cmd = input("\n> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if cmd in ("quit", "exit", "q"):
            print("Bye!")
            break

        elif cmd == "help":
            print("""
  add           Add a new task
  done <id>     Mark a task as complete
  delete <id>   Delete a task
  all           Show all tasks including completed
  clear         Remove all completed tasks
  quit          Exit
""")

        elif cmd == "add":
            task = input("  Task: ").strip()
            if task:
                todos.append({
                    "id": next_id(todos),
                    "task": task,
                    "done": False,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                save(todos)
                print(f"  Added: {task}")

        elif cmd.startswith("done"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                tid = int(parts[1])
                for t in todos:
                    if t["id"] == tid:
                        t["done"] = True
                        save(todos)
                        print(f"  Done: {t['task']}")
                        break
                else:
                    print(f"  No task with id {tid}.")
            else:
                print("  Usage: done <id>")

        elif cmd.startswith("delete"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                tid = int(parts[1])
                remaining = [t for t in todos if t["id"] != tid]
                if len(remaining) == len(todos):
                    print(f"  No task with id {tid}.")
                else:
                    removed = next(t for t in todos if t["id"] == tid)
                    save(remaining)
                    print(f"  Deleted: {removed['task']}")
            else:
                print("  Usage: delete <id>")

        elif cmd == "all":
            show(todos, show_all=True)

        elif cmd == "clear":
            remaining = [t for t in todos if not t["done"]]
            removed = len(todos) - len(remaining)
            save(remaining)
            print(f"  Cleared {removed} completed task(s).")

        elif cmd == "":
            continue

        else:
            print(f"  Unknown command: '{cmd}'. Type 'help' for options.")


if __name__ == "__main__":
    main()
