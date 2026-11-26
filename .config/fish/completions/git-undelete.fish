complete -c git-undelete -f -n '__fish_is_nth_token 1' -a '(__fish_git_custom_deleted_files)' -d 'Deleted path to restore'
