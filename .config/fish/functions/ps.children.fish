# Defined via `source`
function ps.children
    for p in $argv
        cat /proc/$p/task/*/children | tr '\ ' '\n'
    end
end
