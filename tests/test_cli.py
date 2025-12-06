"""Integration tests for CLI."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Get project root for PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def temp_tasks_file(tmp_path: Path):
    """Set up temporary tasks file."""
    return tmp_path / "tasks.json"


def run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run CLI with proper PYTHONPATH."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    return subprocess.run(
        [sys.executable, "-m", "src.cli", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )


class TestCliAddTask:
    def test_add_task_via_cli(self, temp_tasks_file: Path):
        result = run_cli(["add", "Buy groceries"], temp_tasks_file.parent)

        assert result.returncode == 0
        assert "Added" in result.stdout

    def test_add_task_creates_file(self, temp_tasks_file: Path):
        run_cli(["add", "Test task"], temp_tasks_file.parent)

        assert temp_tasks_file.exists()

        with open(temp_tasks_file) as f:
            data = json.load(f)

        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test task"

    def test_add_multiple_tasks(self, temp_tasks_file: Path):
        for title in ["Task 1", "Task 2", "Task 3"]:
            run_cli(["add", title], temp_tasks_file.parent)

        with open(temp_tasks_file) as f:
            data = json.load(f)

        assert len(data["tasks"]) == 3
