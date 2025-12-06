"""Tests for Task model."""
from datetime import datetime

import pytest

from src.task import Task


class TestTaskCreation:
    def test_task_creation_with_title(self):
        task = Task(title="Buy milk")

        assert task.title == "Buy milk"
        assert task.done is False
        assert task.id is not None
        assert isinstance(task.created_at, datetime)

    def test_task_has_unique_id(self):
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        assert task1.id != task2.id


class TestTaskSerialization:
    def test_task_to_dict(self):
        task = Task(title="Test task")
        data = task.to_dict()

        assert data["title"] == "Test task"
        assert data["done"] is False
        assert "id" in data
        assert "created_at" in data

    def test_task_from_dict(self):
        original = Task(title="Original task")
        data = original.to_dict()

        restored = Task.from_dict(data)

        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.done == original.done
