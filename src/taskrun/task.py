import shlex
import subprocess

from simple_term_menu import TerminalMenu

from taskrun.variables import collect_input_ids, expand_variables


def resolve_inputs(input_ids, inputs_defs):
    """Prompt the user for each required input and return a dict of id -> value."""
    resolved = {}
    for input_id in sorted(input_ids):
        input_def = next((i for i in inputs_defs if i.get("id") == input_id), None)
        if input_def is None:
            continue

        input_type = input_def.get("type", "promptString")
        description = input_def.get("description", input_id)
        default = input_def.get("default", "")

        if input_type == "promptString":
            prompt = description
            if default:
                prompt += f" [{default}]"
            prompt += ": "
            value = input(prompt).strip()
            resolved[input_id] = value if value else default

        elif input_type == "pickString":
            raw_options = input_def.get("options", [])
            labels, values = [], []
            for opt in raw_options:
                if isinstance(opt, str):
                    labels.append(opt)
                    values.append(opt)
                else:
                    label = opt.get("label", opt.get("value", ""))
                    val = opt.get("value", opt.get("label", ""))
                    labels.append(label)
                    values.append(val)

            cursor = values.index(default) if default in values else 0
            print(description)
            terminal_menu = TerminalMenu(labels, cursor_index=cursor)
            choice = terminal_menu.show()
            resolved[input_id] = values[choice] if choice is not None else default

        # "command" input type requires VS Code internals — not supported

    return resolved


class Task:
    def __init__(
        self,
        label,
        command,
        args,
        cwd,
        env,
        task_type,
        depends_on,
        depends_order,
        root_dir,
        hide,
    ):
        self.label = label
        self.command = command  # may still contain ${input:ID}
        self.args = args  # may still contain ${input:ID}
        self.cwd = cwd
        self.env = env
        self.task_type = task_type  # "shell" or "process"
        self.depends_on = depends_on  # list of label strings
        self.depends_order = depends_order  # "parallel" | "sequence"
        self.root_dir = root_dir
        self.hide = hide  # bool — omit from interactive menu

    def run(self, all_tasks=None, inputs_defs=None, _visited=None):
        """Execute the task, running dependsOn tasks first."""
        if _visited is None:
            _visited = set()

        if self.label in _visited:
            print(f"Warning: circular dependency detected for task '{self.label}', skipping.")
            return 0
        _visited.add(self.label)

        # Run dependencies first
        if self.depends_on and all_tasks:
            for dep_label in self.depends_on:
                dep = next((t for t in all_tasks if t.label == dep_label), None)
                if dep is None:
                    print(f"Warning: dependency task '{dep_label}' not found.")
                    continue
                ret = dep.run(all_tasks=all_tasks, inputs_defs=inputs_defs, _visited=set(_visited))
                # For sequence order, stop on failure
                if ret != 0 and self.depends_order == "sequence":
                    print(f"Dependency '{dep_label}' failed (exit {ret}), aborting.")
                    return ret

        # Collect and resolve any ${input:ID} references
        all_strings = [self.command] + self.args
        input_ids = collect_input_ids(all_strings)
        resolved_inputs = {}
        if input_ids and inputs_defs:
            resolved_inputs = resolve_inputs(input_ids, inputs_defs)

        def subst(s):
            return expand_variables(s, self.root_dir, resolved_inputs) if resolved_inputs else s

        command = subst(self.command)
        args = [subst(a) for a in self.args]
        cwd = self.cwd

        print(f"Running task: {self.label}")

        if self.task_type == "process":
            cmd = [command] + args
            print(f"Command: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, cwd=cwd, env=self.env)
        else:
            # shell type: append args to the command string
            if args:
                full_cmd = command + " " + " ".join(shlex.quote(a) for a in args)
            else:
                full_cmd = command
            print(f"Command: {full_cmd}")
            process = subprocess.Popen(full_cmd, cwd=cwd, env=self.env, shell=True)

        process.wait()
        return process.returncode
