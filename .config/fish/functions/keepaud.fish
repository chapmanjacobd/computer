# Defined interactively
function keepaud
    set dest $argv[2]
    or set dest ~/d/85_Inspiration/ffa/

    cp $argv[1] $dest
    set f (basename $argv[1])
    ffa "$dest/$f"
    and /bin/rm $argv[1]
end
