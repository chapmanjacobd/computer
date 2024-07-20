# Defined interactively
function trash-size
    for f in (trash-list --trash-dirs)
        echo $f
        du -hs $f
    end
end
