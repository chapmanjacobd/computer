# Defined interactively
function keepaud
    set dest (coalesce $argv[2] ~/d/archive/audio/other/)

    cp $argv[1] $dest
    set f (basename $argv[1])

    if has_video "$dest/$f"
        ffa "$dest/$f"
        and /bin/rm "$dest/$f"
    end

    /bin/rm $argv[1]    
end
