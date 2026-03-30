# Defined interactively
function cd.audio.dump
    (nofs which check/internals/audio/)
    whipper cd cd.audio.dump --offset=+6
    echo 'remember to copy to library'
    echo cp -r ./ (d dump/audio/music/)
end
