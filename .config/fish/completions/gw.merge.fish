complete -c gw.merge -f -a '(git worktree list --porcelain 2>/dev/null | string match -r "^branch refs/heads/.*" | string replace "branch refs/heads/" "")' -d 'Worktree branch'
