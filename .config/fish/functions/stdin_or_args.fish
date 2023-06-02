# Defined interactively
function stdin_or_args
    if test (count $argv) -eq 0
        cat /dev/stdin
    else
        echo $argv
    end

end
