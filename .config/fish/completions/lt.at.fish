complete -c lt.at -f
complete -c lt.at -n '__fish_is_nth_token 1' -a next -d 'Delete the playing file and go to the next one'
complete -c lt.at -n '__fish_is_nth_token 1' -a stop -d 'Stop playback'
complete -c lt.at -n '__fish_is_nth_token 1' -a pause -d 'Pause playback'
complete -c lt.at -n '__fish_is_nth_token 1' -a play -d 'Resume playback'
complete -c lt.at -n '__fish_is_nth_token 1' -a now -d 'Show what is playing'
