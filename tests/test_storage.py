"""Tests for TaskStorage."""
import json
from pathlib import Path

import pytest

from src.storage import TaskStorage
from src.task import Task


@pytest.fixture
def temp_storage(tmp_path: Path) -> TaskStorage:
    """Create storage with temporary file."""
    storage_file = tmp_path / "tasks.json"
    return TaskStorage(storage_file)


class TestStorageAddTask:
    def test_add_task_creates_file(self, temp_storage: TaskStorage):
        task = Task(title="New task")

        temp_storage.add_task(task)

        assert temp_storage.path.exists()

    def test_add_task_saves_to_file(self, temp_storage: TaskStorage):
        task = Task(title="Saved task")

        temp_storage.add_task(task)

        with open(temp_storage.path) as f:
            data = json.load(f)

        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Saved task"


class TestStoragePersistence:
    def test_load_empty_storage(self, temp_storage: TaskStorage):
        tasks = temp_storage.load()

        assert tasks == []

    def test_save_and_load_tasks(self, temp_storage: TaskStorage):
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        temp_storage.add_task(task1)
        temp_storage.add_task(task2)

        # Create new storage instance to test loading
        new_storage = TaskStorage(temp_storage.path)
        loaded_tasks = new_storage.load()

        assert len(loaded_tasks) == 2
        assert loaded_tasks[0].title == "Task 1"
        assert loaded_tasks[1].title == "Task 2"
