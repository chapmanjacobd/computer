complete -c stickysync -s v -l verbose -d 'Increase verbosity'
complete -c stickysync -n '__fish_is_nth_token 2' -a '(__fish_complete_directories)' -d 'Source directory'
complete -c stickysync -n '__fish_is_nth_token 3' -a '(__fish_complete_directories)' -d 'Destination directory'
