function toAudio
    ffmpeg -i $argv[1] $argv[2]$argv[1].oga
end
