complete -c git-rebranch -f
complete -c git-rebranch -l dry-run -d 'Show the plan without rebasing'
complete -c git-rebranch -n '__fish_is_nth_token 1' -a '(__fish_git_custom_local_branches)' -d 'Branch to flatten'
