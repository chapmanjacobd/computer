complete -c git-reset-author -f -n '__fish_is_nth_token 1' -a '(__fish_git_custom_revisions)' -d 'Oldest commit to rewrite'
