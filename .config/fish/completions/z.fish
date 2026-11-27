complete -c z -f
complete -c z -n '__fish_is_nth_token 1' -a '(__fish_complete_directories)' -d 'Directory query'
complete -c z -n '__fish_is_nth_token 2' -a '(__fish_git_custom_branches)' -d 'Branch worktree'
