complete -c git-wip-message -f
complete -c git-wip-message -l staged -d 'Describe staged changes instead of a commit'
complete -c git-wip-message -n '__fish_is_nth_token 1' -a '(__fish_git_custom_revisions)' -d 'Commit to describe'
