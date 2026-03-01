" taskrun.vim — Vim plugin for taskrun
" Requires: vim-dispatch (https://github.com/tpope/vim-dispatch)

if exists('g:loaded_taskrun')
  finish
endif
let g:loaded_taskrun = 1

" Check for vim-dispatch
if !exists(':Dispatch')
  echoerr 'taskrun.vim requires vim-dispatch. See https://github.com/tpope/vim-dispatch'
  finish
endif

" Return the taskrun executable path (override with g:taskrun_executable)
function! s:Executable()
  return get(g:, 'taskrun_executable', 'taskrun')
endfunction

" Populate completion list from `taskrun --list`
function! TaskrunComplete(ArgLead, CmdLine, CursorPos)
  let l:exe = s:Executable()
  let l:tasks = systemlist(l:exe . ' --list 2>/dev/null')
  if v:shell_error != 0
    return []
  endif
  if a:ArgLead ==# ''
    return l:tasks
  endif
  return filter(copy(l:tasks), 'v:val =~# "^" . a:ArgLead')
endfunction

" Run a task asynchronously via vim-dispatch
function! s:RunTask(task)
  if a:task ==# ''
    echohl ErrorMsg
    echom 'taskrun: no task specified. Usage: :Taskrun <task>'
    echohl None
    return
  endif
  let l:exe = s:Executable()
  execute 'Dispatch ' . l:exe . ' --label ' . shellescape(a:task)
endfunction

" Interactively choose a task and dispatch it
function! s:ChooseAndRun()
  let l:exe = s:Executable()
  let l:choice = trim(system(l:exe . ' --choice-only'))
  if v:shell_error != 0 || l:choice ==# ''
    return
  endif
  execute 'Dispatch ' . l:exe . ' --label ' . shellescape(l:choice)
endfunction

" :Taskrun <task>   — run a task asynchronously with tab-completion
" :Taskrun!         — interactively choose a task, then dispatch it
command! -bang -nargs=? -complete=customlist,TaskrunComplete Taskrun
      \ if <bang>0 && <q-args> ==# '' |
      \   call s:ChooseAndRun() |
      \ elseif <q-args> !=# '' |
      \   call s:RunTask(<q-args>) |
      \ else |
      \   echohl ErrorMsg |
      \   echom 'taskrun: no task specified. Usage: :Taskrun <task> or :Taskrun!' |
      \   echohl None |
      \ endif
