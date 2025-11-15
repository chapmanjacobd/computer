# Defined via `source`
function proc.children
    for p in $argv
        cat /proc/$p/task/*/children | tr '\ ' '\n'
    end
end
