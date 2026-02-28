import hashlib

from taskrun.cache import cache_path, load_cache, save_cache, sort_tasks_by_history
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


class TestCachePath:
    def test_deterministic(self, tmp_path):
        path1 = cache_path("/some/project")
        path2 = cache_path("/some/project")
        assert path1 == path2

    def test_different_roots_give_different_paths(self):
        path1 = cache_path("/project/a")
        path2 = cache_path("/project/b")
        assert path1 != path2

    def test_contains_sha256_prefix(self):
        root = "/my/project"
        expected_hash = hashlib.sha256(root.encode()).hexdigest()[:16]
        path = cache_path(root)
        assert expected_hash in path
        assert path.endswith(".json")


class TestLoadSaveCache:
    def test_load_missing_returns_default(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        root = str(tmp_path / "nonexistent")
        result = load_cache(root)
        assert result == {"root_dir": root, "tasks": {}}

    def test_round_trip(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        root = str(tmp_path / "myproject")
        cache = {
            "root_dir": root,
            "tasks": {
                "build": {"count": 3, "last_run": 1000.0},
                "test": {"count": 1, "last_run": 2000.0},
            },
        }
        save_cache(root, cache)
        loaded = load_cache(root)
        assert loaded == cache


class TestSortTasksByHistory:
    def test_most_recent_first(self):
        tasks = [_make_task("old"), _make_task("new")]
        cache = {
            "tasks": {
                "old": {"count": 5, "last_run": 1000.0},
                "new": {"count": 1, "last_run": 2000.0},
            }
        }
        result = sort_tasks_by_history(tasks, cache)
        assert [t.label for t in result] == ["new", "old"]

    def test_no_history_preserves_order(self):
        tasks = [_make_task("a"), _make_task("b"), _make_task("c")]
        cache = {"tasks": {}}
        result = sort_tasks_by_history(tasks, cache)
        assert [t.label for t in result] == ["a", "b", "c"]

    def test_tasks_with_history_before_without(self):
        tasks = [_make_task("never_run"), _make_task("ran_once")]
        cache = {"tasks": {"ran_once": {"count": 1, "last_run": 500.0}}}
        result = sort_tasks_by_history(tasks, cache)
        assert [t.label for t in result] == ["ran_once", "never_run"]

    def test_empty_cache(self):
        tasks = [_make_task("x"), _make_task("y")]
        result = sort_tasks_by_history(tasks, {})
        assert [t.label for t in result] == ["x", "y"]
