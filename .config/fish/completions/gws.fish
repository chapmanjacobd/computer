complete -c gws -f
complete -c gws -n '__fish_is_nth_token 1' -a '(git worktree list --porcelain 2>/dev/null | string match -r "^worktree .*" | string replace "worktree " "")' -d 'Worktree path'
