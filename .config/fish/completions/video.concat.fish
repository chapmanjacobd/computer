complete -c video.concat -n '__fish_is_nth_token 1' -f -d 'Output file'
complete -c video.concat -n 'not __fish_is_nth_token 1' -f -a '(__fish_complete_suffix .mp4 .mkv .webm .mov)' -d 'Input video'
