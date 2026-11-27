complete -c trash.empty.no.snapshot -f
complete -c trash.empty.no.snapshot -s f -d 'Empty without confirmation'
complete -c trash.empty.no.snapshot -a '(trash-list --trash-dirs 2>/dev/null)' -d 'Trash directory'
