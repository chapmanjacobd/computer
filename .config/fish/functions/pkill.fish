# Defined via `source`
function pkill
    set -l opts
    set -l patterns
    for arg in $argv
        if string match -qr -- '^-' $arg
            set opts $opts $arg
        else
            set patterns $patterns $arg
        end
    end

    if test (count $patterns) -gt 0
        command pkill $opts $patterns
    else
        kill $opts (ps.fzf)
    end
end
