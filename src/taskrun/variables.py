import os
import re


def expand_variables(value, root_dir, resolved_inputs=None):
    """Expand VS Code predefined variables in a string.

    Supports: ${workspaceFolder}, ${workspaceFolderBasename}, ${userHome},
              ${cwd}, ${env:VAR}, and ${input:ID} (when resolved_inputs given).
    """
    home_dir = os.path.expanduser("~")
    cwd = os.getcwd()

    value = value.replace("${userHome}", home_dir)
    value = value.replace("${workspaceFolder}", root_dir)
    value = value.replace("${workspaceFolderBasename}", os.path.basename(root_dir))
    value = value.replace("${cwd}", cwd)

    # Expand ${env:VAR} references
    def expand_env(match):
        return os.environ.get(match.group(1), "")

    value = re.sub(r"\$\{env:([^}]+)\}", expand_env, value)

    # Expand ${input:ID} references if resolved values are provided
    if resolved_inputs:

        def expand_input(match):
            return resolved_inputs.get(match.group(1), match.group(0))

        value = re.sub(r"\$\{input:([^}]+)\}", expand_input, value)

    return value


def collect_input_ids(strings):
    """Return the set of ${input:ID} IDs referenced in any of the given strings."""
    ids = set()
    for s in strings:
        ids.update(re.findall(r"\$\{input:([^}]+)\}", s))
    return ids
