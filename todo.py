#!/usr/bin/env python3
"""A simple CLI todo list stored in a JSON file."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

TODO_FILE = Path.home() / ".todos.json"


def load() -> list[dict]:
    if not TODO_FILE.exists():
        return []
    return json.loads(TODO_FILE.read_text())


def save(todos: list[dict]) -> None:
    TODO_FILE.write_text(json.dumps(todos, indent=2))


def cmd_add(args) -> None:
    todos = load()
    todos.append({
        "id": (max(t["id"] for t in todos) + 1) if todos else 1,
        "task": args.task,
        "done": False,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save(todos)
    print(f"Added: {args.task}")


def cmd_list(args) -> None:
    todos = load()
    if not todos:
        print("No tasks yet. Add one with: python todo.py add \"your task\"")
        return

    if args.all:
        items = todos
    else:
        items = [t for t in todos if not t["done"]]
        if not items:
            print("All tasks are done!")
            return

    for t in items:
        status = "x" if t["done"] else " "
        print(f"  [{status}] {t['id']:>3}.  {t['task']}")


def cmd_done(args) -> None:
    todos = load()
    for t in todos:
        if t["id"] == args.id:
            t["done"] = True
            save(todos)
            print(f"Done: {t['task']}")
            return
    print(f"No task with id {args.id}.")
    sys.exit(1)


def cmd_delete(args) -> None:
    todos = load()
    remaining = [t for t in todos if t["id"] != args.id]
    if len(remaining) == len(todos):
        print(f"No task with id {args.id}.")
        sys.exit(1)
    removed = next(t for t in todos if t["id"] == args.id)
    save(remaining)
    print(f"Deleted: {removed['task']}")


def cmd_clear(args) -> None:
    todos = load()
    remaining = [t for t in todos if not t["done"]]
    removed = len(todos) - len(remaining)
    save(remaining)
    print(f"Cleared {removed} completed task(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple CLI todo list.")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a new task")
    add_p.add_argument("task", help="Task description")

    list_p = sub.add_parser("list", help="List tasks")
    list_p.add_argument("--all", action="store_true", help="Include completed tasks")

    done_p = sub.add_parser("done", help="Mark a task as complete")
    done_p.add_argument("id", type=int, help="Task ID")

    del_p = sub.add_parser("delete", help="Delete a task")
    del_p.add_argument("id", type=int, help="Task ID")

    sub.add_parser("clear", help="Remove all completed tasks")

    args = parser.parse_args()

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "delete": cmd_delete,
        "clear": cmd_clear,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
