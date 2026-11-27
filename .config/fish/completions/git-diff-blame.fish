complete -c git-diff-blame -l staged -d 'Compare against the index'
complete -c git-diff-blame -n '__fish_is_nth_token 1' -f -a '(__fish_git_custom_revisions)' -d 'Base revision'
complete -c git-diff-blame -f -a '(__fish_git_custom_tracked_files)' -d 'Tracked file'
