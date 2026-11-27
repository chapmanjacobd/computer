complete -c zg -f
complete -c zg -n '__fish_is_nth_token 1' -a - -d 'Previous branch'
complete -c zg -n '__fish_is_nth_token 1' -a '(__fish_git_custom_branches)' -d 'Worktree branch'
