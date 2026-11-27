complete -c files.un.mojibake -f
complete -c files.un.mojibake -n '__fish_is_nth_token 1' -a url -d 'Decode URL-escaped filenames'
complete -c files.un.mojibake -n '__fish_is_nth_token 1' -a find -d 'Find a correction from BROKEN to GOOD'
complete -c files.un.mojibake -n '__fish_is_nth_token 3' -a via -d 'Reinterpret ENCODING via ENCODING'
