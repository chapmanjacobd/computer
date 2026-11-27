complete -c gb.switch -f
complete -c gb.switch -n '__fish_is_nth_token 1' -a '(__fish_git_custom_local_branches)' -d 'Local branch to switch to'
