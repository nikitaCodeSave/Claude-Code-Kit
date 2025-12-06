"""JSON storage for tasks."""
import json
from pathlib import Path

from src.task import Task


class TaskStorage:
    """Handles task persistence to JSON file."""

    def __init__(self, path: Path | str = "tasks.json"):
        self.path = Path(path)

    def load(self) -> list[Task]:
        """Load tasks from storage file."""
        if not self.path.exists():
            return []

        with open(self.path) as f:
            data = json.load(f)

        return [Task.from_dict(t) for t in data.get("tasks", [])]

    def save(self, tasks: list[Task]) -> None:
        """Save tasks to storage file."""
        data = {"tasks": [t.to_dict() for t in tasks]}

        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def add_task(self, task: Task) -> None:
        """Add a new task to storage."""
        tasks = self.load()
        tasks.append(task)
        self.save(tasks)
