complete -c mpv.set -f
complete -c mpv.set -n '__fish_is_nth_token 1' -a 'pause volume mute speed fullscreen loop loop-file loop-playlist audio-delay sub-delay chapter playlist-pos' -d 'mpv property'
