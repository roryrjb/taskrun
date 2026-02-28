import json
import os
import platform

from taskrun.parser import get_platform_overrides, get_task_by_label, parse_tasks
from taskrun.task import Task


def _make_task(label):
    return Task(
        label=label,
        command="echo",
        args=[],
        cwd="/tmp",
        env={},
        task_type="shell",
        depends_on=[],
        depends_order="parallel",
        root_dir="/tmp",
        hide=False,
    )


class TestGetTaskByLabel:
    def test_found(self):
        tasks = [_make_task("build"), _make_task("test")]
        assert get_task_by_label(tasks, "test").label == "test"

    def test_not_found(self):
        tasks = [_make_task("build")]
        assert get_task_by_label(tasks, "missing") is None

    def test_empty_list(self):
        assert get_task_by_label([], "anything") is None


class TestGetPlatformOverrides:
    def test_returns_matching_platform(self):
        system = platform.system().lower()
        key = {"linux": "linux", "darwin": "osx", "windows": "windows"}.get(system)
        task_json = {key: {"command": "platform-specific"}}
        result = get_platform_overrides(task_json)
        assert result == {"command": "platform-specific"}

    def test_returns_empty_when_no_match(self):
        task_json = {"nonexistent_platform": {"command": "nope"}}
        result = get_platform_overrides(task_json)
        assert result == {}

    def test_returns_empty_for_empty_task(self):
        assert get_platform_overrides({}) == {}


class TestParseTasks:
    def test_basic_task(self, tmp_path):
        root_dir = str(tmp_path)
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        tasks_file = vscode_dir / "tasks.json"
        tasks_file.write_text(
            json.dumps(
                {
                    "version": "2.0.0",
                    "tasks": [
                        {
                            "label": "build",
                            "type": "shell",
                            "command": "make",
                            "args": ["all"],
                        }
                    ],
                }
            )
        )

        tasks, inputs_defs = parse_tasks(root_dir, str(tasks_file))
        assert len(tasks) == 1
        assert tasks[0].label == "build"
        assert tasks[0].command == "make"
        assert tasks[0].args == ["all"]
        assert tasks[0].task_type == "shell"
        assert tasks[0].depends_on == []
        assert tasks[0].hide is False
        assert inputs_defs == []

    def test_task_with_depends_on(self, tmp_path):
        root_dir = str(tmp_path)
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        tasks_file = vscode_dir / "tasks.json"
        tasks_file.write_text(
            json.dumps(
                {
                    "version": "2.0.0",
                    "tasks": [
                        {"label": "compile", "command": "gcc"},
                        {
                            "label": "test",
                            "command": "ctest",
                            "dependsOn": ["compile"],
                            "dependsOrder": "sequence",
                        },
                    ],
                }
            )
        )

        tasks, _ = parse_tasks(root_dir, str(tasks_file))
        test_task = next(t for t in tasks if t.label == "test")
        assert test_task.depends_on == ["compile"]
        assert test_task.depends_order == "sequence"

    def test_task_with_options_cwd(self, tmp_path):
        root_dir = str(tmp_path)
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        tasks_file = vscode_dir / "tasks.json"
        tasks_file.write_text(
            json.dumps(
                {
                    "version": "2.0.0",
                    "tasks": [
                        {
                            "label": "run",
                            "command": "python",
                            "options": {"cwd": "${workspaceFolder}/src"},
                        }
                    ],
                }
            )
        )

        tasks, _ = parse_tasks(root_dir, str(tasks_file))
        assert tasks[0].cwd == os.path.join(root_dir, "src")

    def test_hidden_task(self, tmp_path):
        root_dir = str(tmp_path)
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        tasks_file = vscode_dir / "tasks.json"
        tasks_file.write_text(
            json.dumps(
                {
                    "version": "2.0.0",
                    "tasks": [{"label": "hidden", "command": "echo", "hide": True}],
                }
            )
        )

        tasks, _ = parse_tasks(root_dir, str(tasks_file))
        assert tasks[0].hide is True

    def test_inputs_returned(self, tmp_path):
        root_dir = str(tmp_path)
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        tasks_file = vscode_dir / "tasks.json"
        tasks_file.write_text(
            json.dumps(
                {
                    "version": "2.0.0",
                    "tasks": [{"label": "greet", "command": "echo ${input:name}"}],
                    "inputs": [
                        {
                            "id": "name",
                            "type": "promptString",
                            "description": "Your name",
                        }
                    ],
                }
            )
        )

        _, inputs_defs = parse_tasks(root_dir, str(tasks_file))
        assert len(inputs_defs) == 1
        assert inputs_defs[0]["id"] == "name"

    def test_depends_on_string_normalized_to_list(self, tmp_path):
        root_dir = str(tmp_path)
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        tasks_file = vscode_dir / "tasks.json"
        tasks_file.write_text(
            json.dumps(
                {
                    "version": "2.0.0",
                    "tasks": [
                        {"label": "deploy", "command": "deploy.sh", "dependsOn": "build"}
                    ],
                }
            )
        )

        tasks, _ = parse_tasks(root_dir, str(tasks_file))
        assert tasks[0].depends_on == ["build"]
