# taskrun

Taskrun is a (currently) very simple task runner that looks for `.vscode/tasks.json` files in your project and allows you to interactively run them. 

## Current Limitations

* Unix only, since it relies on [simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu) which doesn't work on Windows.
* Only partial coverage of VS code tasks spec

## Future Development

I'm mostly using Windows nowadays (no, not WSL) and I've yet to find a suitable replacement for __simple-term-menu__ that works there, so for the time being, development has stalled.
