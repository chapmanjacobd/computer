complete -c mpvctl -f
complete -c mpvctl -s h -l help -d 'Show help'
complete -c mpvctl -n '__fish_is_nth_token 1' -a next -d 'Play the next playlist item'
complete -c mpvctl -n '__fish_is_nth_token 1' -a previous -d 'Play the previous playlist item'
complete -c mpvctl -n '__fish_is_nth_token 1' -a play-pause -d 'Toggle playback'
complete -c mpvctl -n '__fish_is_nth_token 1' -a play -d 'Resume playback'
complete -c mpvctl -n '__fish_is_nth_token 1' -a pause -d 'Pause playback'
complete -c mpvctl -n '__fish_is_nth_token 1' -a stop -d 'Quit mpv'
