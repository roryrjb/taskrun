# taskrun

Taskrun is a (currently) very simple task runner that looks for `.vscode/tasks.json` files in your project and allows you to interactively run them.

## Dependencies

* [uv](https://docs.astral.sh/uv/) — required to run the script (uses `uv run --script`)

## Current Limitations

* Unix only, since it relies on [simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu) which doesn't work on Windows.
* Only partial coverage of VS code tasks spec
