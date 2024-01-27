# Defined interactively
function to_sync
    set path "$argv"
    set -l tasks sync/ dump/ pending/ check/ library/ archive/

    for r in $tasks
        if string match -r -- $r $path >/dev/null
            set path (string replace -r $r 'sync/' $path)
        end
    end

    mkdir (path dirname "$path")
    mv "$argv" "$path"
end
