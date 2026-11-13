function ffmpeg.audio.split.93
    for file in $argv
        ffmpeg -y -i $file -filter_complex "compand=attacks=0:points=-80/-900|-45/-15|-27/-9|0/-7|20/-7:gain=5" -c:a libopus -f segment -segment_time 93 (path.withsuffix .%09d -e opus "$file")
    end
end
