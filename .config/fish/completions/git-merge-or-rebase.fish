complete -c git-merge-or-rebase -f
complete -c git-merge-or-rebase -s n -l no-fetch -d 'Do not fetch the target remote first'
complete -c git-merge-or-rebase -l no-imerge -d 'Use a plain merge instead of git-imerge'
complete -c git-merge-or-rebase -s h -l help -d 'Show usage'
complete -c git-merge-or-rebase -n '__fish_is_nth_token 1' -a '(__fish_git_custom_branches)' -d 'Branch to sync with'
