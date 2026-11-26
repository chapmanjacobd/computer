complete -c git-push-until -s f -l force -d 'Allow rewinding the remote branch (uses --force-with-lease)'
complete -c git-push-until -s n -l dry-run -d 'Print the push command instead of running it'
complete -c git-push-until -s h -l help -d 'Show usage'

complete -c git-push-until -f -n '__fish_is_nth_token 1' -a '(__fish_git_custom_revisions)' -d 'Last commit to push'
complete -c git-push-until -f -n '__fish_is_nth_token 2' -a '(__fish_git_custom_remotes)' -d 'Remote to push to'
complete -c git-push-until -f -n '__fish_is_nth_token 3' -a '(__fish_git_custom_local_branches)' -d 'Remote branch name'
