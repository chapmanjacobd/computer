complete -c git-pop -f
complete -c git-pop -n '__fish_is_nth_token 2' -a '(__fish_git_custom_revisions)' -d 'Commit to branch from'
