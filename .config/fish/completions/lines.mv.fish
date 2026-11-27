complete -c lines.mv -s s -l search -x -d 'Move only lines matching this regex'
complete -c lines.mv -s h -l help -d 'Show help'
complete -c lines.mv -n '__fish_is_nth_token 1' -F -d 'Source file'
complete -c lines.mv -n '__fish_is_nth_token 2' -F -d 'Destination file'
