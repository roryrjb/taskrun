import hashlib
import json
import os
import time


def cache_path(root_dir):
    """Return the path to the cache file for a given project root."""
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "taskrun")
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.sha256(root_dir.encode()).hexdigest()[:16]
    return os.path.join(cache_dir, f"{key}.json")


def load_cache(root_dir):
    """Load task run history for the given project root."""
    path = cache_path(root_dir)
    if os.path.exists(path):
        try:
            with open(path, "r") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {"root_dir": root_dir, "tasks": {}}


def save_cache(root_dir, cache):
    """Persist task run history for the given project root."""
    path = cache_path(root_dir)
    try:
        with open(path, "w") as fh:
            json.dump(cache, fh, indent=2)
    except OSError:
        pass


def record_task_run(root_dir, label):
    """Increment the run count and update last_run timestamp for a task."""
    cache = load_cache(root_dir)
    stats = cache["tasks"].get(label, {"count": 0, "last_run": None})
    stats["count"] += 1
    stats["last_run"] = time.time()
    cache["tasks"][label] = stats
    save_cache(root_dir, cache)


def sort_tasks_by_history(tasks, cache):
    """Sort tasks: most-recently-run first, then by invocation count, then original order."""
    task_stats = cache.get("tasks", {})

    def sort_key(item):
        index, task = item
        stats = task_stats.get(task.label, {})
        last_run = stats.get("last_run")
        count = stats.get("count", 0)
        if last_run is None:
            return (1, 0, index)
        return (0, -last_run, -count)

    return [task for _, task in sorted(enumerate(tasks), key=sort_key)]
