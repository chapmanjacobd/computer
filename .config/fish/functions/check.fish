# Defined interactively
function check
    set path (path resolve "$argv")
    set -l tasks sync/ dump/ pending/ check/ library/ archive/

    for r in $tasks
        if string match -r -- $r $path >/dev/null
            set path (string replace -r $r 'check/' $path)
        end
    end

    mv "$argv" "$path"
end
