import os
import platform

import json5

from taskrun.task import Task
from taskrun.variables import expand_variables


def get_platform_overrides(task_json):
    """Return the platform-specific override block for the current OS, or {}."""
    system = platform.system().lower()
    key = {"linux": "linux", "darwin": "osx", "windows": "windows"}.get(system)
    return task_json.get(key, {}) if key else {}


def parse_tasks(root_dir, file_path):
    """Parse .vscode/tasks.json; return (list[Task], list[input_def])."""
    with open(file_path, "r") as fh:
        data = json5.load(fh)

    inputs_defs = data.get("inputs", [])
    tasks = []

    for task_json in data.get("tasks", []):
        label = task_json.get("label", "")

        # Platform-specific overrides (linux / osx / windows)
        overrides = get_platform_overrides(task_json)

        def field(key, default=None):
            """Return platform override if present, otherwise task-level value."""
            return overrides.get(key, task_json.get(key, default))

        task_type = field("type", "shell")
        command = field("command", "")
        args = field("args", [])

        # Expand predefined variables at parse time (${input:ID} deferred to run time)
        command = expand_variables(str(command), root_dir)
        args = [expand_variables(str(a), root_dir) for a in args]

        # Merge options: task-level first, then platform overrides on top
        options = {**task_json.get("options", {}), **overrides.get("options", {})}
        cwd = expand_variables(options.get("cwd", root_dir), root_dir)

        environ = os.environ.copy()
        for key, value in options.get("env", {}).items():
            environ[key] = expand_variables(str(value), root_dir)

        depends_on_raw = field("dependsOn", [])
        depends_on = [depends_on_raw] if isinstance(depends_on_raw, str) else list(depends_on_raw)
        depends_order = field("dependsOrder", "parallel")

        hide = bool(field("hide", False))

        tasks.append(
            Task(
                label=label,
                command=command,
                args=args,
                cwd=cwd,
                env=environ,
                task_type=task_type,
                depends_on=depends_on,
                depends_order=depends_order,
                root_dir=root_dir,
                hide=hide,
            )
        )

    return tasks, inputs_defs


def get_task_by_label(tasks, label):
    for task in tasks:
        if task.label == label:
            return task
    return None


def list_task_labels(tasks):
    for task in tasks:
        print(task.label)


def find_vscode_tasks():
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")

    while current_dir != home_dir:
        tasks_json_path = os.path.join(current_dir, ".vscode", "tasks.json")
        if os.path.exists(tasks_json_path):
            print(f"Found: {tasks_json_path}")
            return tasks_json_path
        current_dir = os.path.dirname(current_dir)

    print("tasks.json not found in any .vscode directory up to the home directory.")
    return None
