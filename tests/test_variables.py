import os

from taskrun.variables import collect_input_ids, expand_variables


class TestCollectInputIds:
    def test_no_ids(self):
        assert collect_input_ids(["plain text", "no variables here"]) == set()

    def test_single_id(self):
        assert collect_input_ids(["${input:myVar}"]) == {"myVar"}

    def test_multiple_ids(self):
        result = collect_input_ids(["${input:foo} and ${input:bar}"])
        assert result == {"foo", "bar"}

    def test_ids_across_strings(self):
        result = collect_input_ids(["${input:a}", "${input:b}"])
        assert result == {"a", "b"}

    def test_duplicates_collapsed(self):
        result = collect_input_ids(["${input:x}", "${input:x} again"])
        assert result == {"x"}

    def test_empty_list(self):
        assert collect_input_ids([]) == set()


class TestExpandVariables:
    def test_workspace_folder(self):
        result = expand_variables("${workspaceFolder}/src", "/my/project")
        assert result == "/my/project/src"

    def test_workspace_folder_basename(self):
        result = expand_variables("${workspaceFolderBasename}", "/my/project")
        assert result == "project"

    def test_user_home(self):
        result = expand_variables("${userHome}/.config", "/root")
        assert result == os.path.expanduser("~") + "/.config"

    def test_cwd(self):
        result = expand_variables("${cwd}", "/root")
        assert result == os.getcwd()

    def test_env_variable(self, monkeypatch):
        monkeypatch.setenv("TASKRUN_TEST_VAR", "hello")
        result = expand_variables("${env:TASKRUN_TEST_VAR}", "/root")
        assert result == "hello"

    def test_env_variable_missing(self):
        result = expand_variables("${env:VERY_UNLIKELY_VAR_12345}", "/root")
        assert result == ""

    def test_input_with_resolved(self):
        resolved = {"name": "world"}
        result = expand_variables("hello ${input:name}", "/root", resolved)
        assert result == "hello world"

    def test_input_unresolved_left_intact(self):
        result = expand_variables("${input:missing}", "/root", {"other": "val"})
        assert result == "${input:missing}"

    def test_input_without_resolved_inputs(self):
        result = expand_variables("${input:x}", "/root")
        assert result == "${input:x}"

    def test_multiple_variables(self):
        result = expand_variables(
            "${workspaceFolder}/build/${workspaceFolderBasename}",
            "/home/user/myproject",
        )
        assert result == "/home/user/myproject/build/myproject"

    def test_no_variables(self):
        result = expand_variables("plain string", "/root")
        assert result == "plain string"
