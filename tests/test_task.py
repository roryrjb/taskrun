from taskrun.task import Task


class TestTaskInit:
    def test_attributes_stored(self):
        env = {"PATH": "/usr/bin"}
        task = Task(
            label="build",
            command="make",
            args=["-j4", "all"],
            cwd="/project",
            env=env,
            task_type="process",
            depends_on=["clean"],
            depends_order="sequence",
            root_dir="/project",
            hide=True,
        )
        assert task.label == "build"
        assert task.command == "make"
        assert task.args == ["-j4", "all"]
        assert task.cwd == "/project"
        assert task.env is env
        assert task.task_type == "process"
        assert task.depends_on == ["clean"]
        assert task.depends_order == "sequence"
        assert task.root_dir == "/project"
        assert task.hide is True

    def test_shell_type(self):
        task = Task(
            label="lint",
            command="ruff check .",
            args=[],
            cwd="/src",
            env={},
            task_type="shell",
            depends_on=[],
            depends_order="parallel",
            root_dir="/src",
            hide=False,
        )
        assert task.task_type == "shell"
        assert task.depends_on == []
        assert task.hide is False
