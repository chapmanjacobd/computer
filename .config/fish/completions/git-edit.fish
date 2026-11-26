complete -c git-edit -f
complete -c git-edit -s h -l help -d 'Show usage'
complete -c git-edit -n '__fish_is_nth_token 1' -a '(__fish_git_custom_revisions)' -d 'Commit to edit'
