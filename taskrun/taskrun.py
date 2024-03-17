#!/usr/bin/env python3

import json
import os
import subprocess
import argparse
import sys
from simple_term_menu import TerminalMenu


class Task:
    def __init__(self, label, command, cwd, env=None):
        self.label = label
        self.command = command
        self.cwd = cwd
        self.env = env if env is not None else os.environ.copy()

    def run(self):
        print(f"Running task: {self.label}")
        print(f"Command: {self.command}")
        process = subprocess.Popen(self.command, cwd=self.cwd, env=self.env, shell=True)
        process.wait()


def parse_tasks(root_dir, file_path):
    # root dir is the parent of the .vscode dir that this file lives in

    with open(file_path, "r") as file:
        data = json.load(file)
        tasks = []
        for task_json in data.get("tasks", []):
            label = task_json.get("label")
            command = (
                task_json.get("command")
                .replace("${userHome}", os.path.expanduser("~"))
                .replace("${workspaceFolder}", root_dir)
            )
            cwd = (
                task_json.get("options", {})
                .get("cwd", os.getcwd())
                .replace("${userHome}", os.path.expanduser("~"))
                .replace("${workspaceFolder}", root_dir)
            )
            environ = os.environ.copy()
            env = task_json.get("options", {}).get("env", {})

            # go through all env variables and expand any that are in the form ${VAR}
            for key, value in env.items():
                environ[key] = value.replace(
                    "${userHome}", os.path.expanduser("~")
                ).replace("${workspaceFolder}", root_dir)

            task = Task(label, command, cwd, environ)
            tasks.append(task)
        return tasks


def get_task_by_label(tasks, label):
    for task in tasks:
        if task.label == label:
            return task
    return None


def list_task_labels(tasks):
    for task in tasks:
        print(task.label)


def find_vscode_tasks():
    # Get the current working directory and the home directory
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")

    # Walk up from the current directory
    while current_dir != home_dir:
        # Construct the .vscode/tasks.json path for the current directory
        tasks_json_path = os.path.join(current_dir, ".vscode", "tasks.json")

        # Check if the tasks.json file exists
        if os.path.exists(tasks_json_path):
            print(f"Found: {tasks_json_path}")
            return tasks_json_path

        # Move up one directory
        current_dir = os.path.dirname(current_dir)

    # If we get here, the file was not found
    print("tasks.json not found in any .vscode directory up to the home directory.")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Run or list VS Code tasks from tasks.json"
    )
    parser.add_argument("--label", help="Label of the task to run", type=str)
    parser.add_argument("--list", help="List all task labels", action="store_true")
    parser.add_argument("--edit", help="Edit tasks.json file", action="store_true")
    args = parser.parse_args()

    file_path = find_vscode_tasks()

    if file_path is None:
        sys.exit(1)

    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(file_path)))
    tasks = parse_tasks(root_dir, file_path)

    if args.edit:
        subprocess.call(os.environ.get("EDITOR", "vim").split(" ") + [file_path])
    elif args.list:
        list_task_labels(tasks)
    else:
        task_to_run = None
        if args.label:
            task_to_run = get_task_by_label(tasks, args.label)
            if not task_to_run:
                print(f"No task found with label: {args.label}")
        elif len(tasks) == 1:
            task_to_run = tasks[0]
        else:
            terminal_menu = TerminalMenu(
                [task.label for task in tasks], search_key=None
            )
            choice = terminal_menu.show()

            if choice is not None:
                task_to_run = tasks[choice]

        if task_to_run:
            task_to_run.run()
        else:
            print("No task to run.")


if __name__ == "__main__":
    main()
