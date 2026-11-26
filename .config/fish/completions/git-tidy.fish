complete -c git-tidy -f
complete -c git-tidy -l dry-run -d 'Show what would happen without changing anything'
complete -c git-tidy -l no-fetch -d 'Skip fetching remotes'
complete -c git-tidy -s y -l yes -d 'Assume yes for prompts'
complete -c git-tidy -n '__fish_is_nth_token 1' -a '(__fish_git_custom_branches)' -d 'Merge target'
