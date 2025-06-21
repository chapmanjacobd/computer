# Defined interactively
function mpvf
    for f in $argv/*
        mpv $f
        confirm
    end
end
