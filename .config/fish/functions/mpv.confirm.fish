# Defined interactively
function mpv.confirm
    for f in $argv/*
        mpv $f
        confirm
    end
end
