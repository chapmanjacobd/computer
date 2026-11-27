complete -c trash.empty -f
complete -c trash.empty -s f -d 'Empty without confirmation'
complete -c trash.empty -a '(trash-list --trash-dirs 2>/dev/null)' -d 'Trash directory'
