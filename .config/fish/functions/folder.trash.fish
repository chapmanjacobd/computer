# Defined interactively
function folder.trash
    set dir "$argv"
    if test ! -d "$dir"
        set dir (path dirname "$argv")
    end

    lb filesystem usage "$dir"

    if gum confirm --default=no "Confirm delete"
        trash "$dir"
    end
end
