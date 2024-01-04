# Defined interactively
function archive
    set path "$argv"
    set -l tasks sync/ dump/ pending/ check/ library/ archive/

    for r in $tasks
        if string match -r -- $r $path >/dev/null
            set path (string replace -r $r 'archive/' $path)
        end
    end

    mv "$argv" "$path"
end
