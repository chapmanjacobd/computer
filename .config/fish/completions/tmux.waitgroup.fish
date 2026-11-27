complete -c tmux.waitgroup -f
complete -c tmux.waitgroup -l interval -x -d 'Seconds between pane checks (default: 0.2)'
complete -c tmux.waitgroup -a '(__fish_complete_command)' -d 'Command to run in a new tmux window'
