complete -c git-create -f
complete -c git-create -n '__fish_is_nth_token 2' -a '(__fish_git_custom_revisions)' -d 'Start point for the new branch'
