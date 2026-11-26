complete -c git-diff-branch -f -n '__fish_is_nth_token 1' -a '(__fish_git_custom_branches)' -d 'Base branch'
complete -c git-diff-branch -w 'git diff'
