complete -c etc.apply -f
complete -c etc.apply -s n -l dry-run -d 'Show diffs without applying changes'
complete -c etc.apply -s y -l yes -d 'Apply all changes without prompting'
complete -c etc.apply -s r -l reload -d 'Reload changed systemd, sysctl, journald, and sshd config'
complete -c etc.apply -s v -l verbose -d 'Print unchanged files too'
complete -c etc.apply -s h -l help -d 'Show usage'
