# taskrun

Taskrun is a (currently) very simple task runner that looks for `.vscode/tasks.json` files in your project and allows you to interactively run them.

## Installation

### Recommended: uv tool install

```sh
uv tool install git+https://github.com/roryrjb/taskrun
```

### pip/x install

```sh
pip/x install git+https://github.com/roryrjb/taskrun
```

### From source

```sh
git clone https://github.com/roryrjb/taskrun
cd taskrun
uv tool install .
```

Make sure `~/.local/bin` is on your `$PATH`.

## Current Limitations

* Unix only, since it relies on [simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu) which doesn't work on Windows.
* Only partial coverage of VS code tasks spec, partly by design, partly by omission

## Vim Plugin

This repository doubles as a Vim plugin that provides an async `:Taskrun` command with tab-completion powered by `taskrun --list`.

### Requirements

* [vim-dispatch](https://github.com/tpope/vim-dispatch) — used to run tasks asynchronously

### Installation

Using [vim-plug](https://github.com/junegunn/vim-plug):

```vim
Plug 'tpope/vim-dispatch'          " required dependency
Plug 'roryrjb/taskrun'
```

After adding the lines to your `~/.vimrc` (or `~/.config/nvim/init.vim`), reload the config and run `:PlugInstall`.

### Usage

Run a task by name:

```vim
:Taskrun build
```

Tab-complete available tasks (populated from `taskrun --list`):

```vim
:Taskrun <Tab>
```

To map a leader shortcut that prompts for a task with completion:

```vim
nnoremap <leader>t :Taskrun<Space>
```

By default the plugin calls `taskrun` from your `$PATH`. If your installation lives elsewhere, point the plugin at it:

```vim
let g:taskrun_executable = '/path/to/taskrun'
```
