# Defined interactively
function trash.inspect
    for d in (trash-list --trash-dirs)
        NO_COLOR=1 ncdu "$d"
    end
end
