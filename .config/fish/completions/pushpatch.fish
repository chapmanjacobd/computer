complete -c pushpatch -f
complete -c pushpatch -s m -l message -r -d 'Commit message (repeatable)'
complete -c pushpatch -s r -l remote -x -a '(__fish_git_custom_remotes)' -d 'Remote to push to (default: origin)'
complete -c pushpatch -s p -l prefix -x -d 'Branch name prefix (default: patch)'
complete -c pushpatch -s h -l help -d 'Show help'
