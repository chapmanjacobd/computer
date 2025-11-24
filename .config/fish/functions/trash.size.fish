# Defined interactively
function trash.size
    for f in (trash-list --trash-dirs)
        du -hs $f | grep -v ^0
    end
end
