# Defined interactively
function tolibrary
    set path (path resolve "$argv")
    set -l tasks sync/ dump/ pending/ check/ library/ archive/

    for r in $tasks
        if string match -r -- $r $path >/dev/null
            set path (string replace -r $r 'library/' $path)
        end
    end
    mkdir (path dirname "$path")

    mv "$argv" "$path"
end
