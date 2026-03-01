import argparse
import os
import subprocess
import sys

from simple_term_menu import TerminalMenu

from taskrun.cache import load_cache, record_task_run, sort_tasks_by_history
from taskrun.parser import find_vscode_tasks, get_task_by_label, list_task_labels, parse_tasks


def main():
    parser = argparse.ArgumentParser(description="Run or list VS Code tasks from tasks.json")
    parser.add_argument("--label", help="Label of the task to run", type=str)
    parser.add_argument("--list", help="List all task labels", action="store_true")
    parser.add_argument("--edit", help="Edit tasks.json file", action="store_true")
    parser.add_argument(
        "--choice-only",
        help="Print chosen task label without running it",
        action="store_true",
    )
    args = parser.parse_args()

    file_path = find_vscode_tasks()
    if file_path is None:
        sys.exit(1)

    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(file_path)))
    tasks, inputs_defs = parse_tasks(root_dir, file_path)
    cache = load_cache(root_dir)

    if args.edit:
        subprocess.call(os.environ.get("EDITOR", "vim").split(" ") + [file_path])
        return

    if args.list:
        visible = [t for t in tasks if not t.hide]
        list_task_labels(sort_tasks_by_history(visible, cache))
        return

    task_to_run = None

    if args.label:
        task_to_run = get_task_by_label(tasks, args.label)
        if not task_to_run:
            print(f"No task found with label: {args.label}")
    elif len(tasks) == 1:
        task_to_run = tasks[0]
    else:
        # Show only non-hidden tasks in the interactive menu, sorted by history
        visible = sort_tasks_by_history([t for t in tasks if not t.hide], cache)
        if not visible:
            print("No tasks available.")
            return
        terminal_menu = TerminalMenu([t.label for t in visible], search_key=None)
        try:
            choice = terminal_menu.show()
            if choice is not None:
                task_to_run = visible[choice]
        except ValueError:
            sys.exit(0)

    if task_to_run:
        if args.choice_only:
            print(task_to_run.label)
            return
        record_task_run(root_dir, task_to_run.label)
        task_to_run.run(all_tasks=tasks, inputs_defs=inputs_defs)
    else:
        print("No task to run.")


if __name__ == "__main__":
    main()
