# Defined interactively
function trash-size
    for f in ~/.local/share/Trash/ /mnt/d/.Trash/
        echo $f
        du -hs $f
    end
end
