# Defined interactively
function cb.file --wraps='cb'
    if status --is-command-substitution
        cb | psub $argv
    else
        cat $argv | cb
    end
end
