function audio.fixup.compand --argument in out
    ffmpeg -i $in -filter_complex "compand=attacks=0:points=-80/-900|-45/-15|-27/-9|0/-7|20/-7:gain=5" -c:v copy -c:a libvorbis $out
end
