# Defined in - @ line 2
function ffclip
    ffmpeg -i "$argv[1]" -ss "$argv[2]". -c copy -to "$argv[3]". (fileSuffix "$argv[1]" "$argv[4]")
end
