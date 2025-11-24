# Defined via `source`
function d.expand
    set path (path resolve "$argv")
    set -l tasks sync/ dump/ pending/ check/ library/ archive/

    for r in $tasks
        if string match -r -- $r $path >/dev/null
            for rn in $tasks
                set np (string replace -r $r $rn $path)
                if test -d $np
                    echo $np
                end
            end
        end
    end
end
