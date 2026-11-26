complete -c git-status-filter -f -n '__fish_is_nth_token 1' -a '(__fish_git_custom_status_codes)' -d 'Index status'
complete -c git-status-filter -f -n '__fish_is_nth_token 2' -a '(__fish_git_custom_status_codes)' -d 'Worktree status'
