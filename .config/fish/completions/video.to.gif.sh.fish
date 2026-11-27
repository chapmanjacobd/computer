complete -c video.to.gif.sh -f
complete -c video.to.gif.sh -n '__fish_is_nth_token 1' -a '(__fish_complete_suffix .mp4 .mkv .webm .mov .avi)' -d 'Input video'
