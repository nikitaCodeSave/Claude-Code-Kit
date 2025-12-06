"""CLI interface for task-cli."""
import argparse
import sys

from src.storage import TaskStorage
from src.task import Task


def main(args: list[str] | None = None) -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="task",
        description="Simple task manager CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")

    parsed = parser.parse_args(args)

    storage = TaskStorage()

    if parsed.command == "add":
        task = Task(title=parsed.title)
        storage.add_task(task)
        print(f"Added task: {task.title}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
