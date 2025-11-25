# Defined interactively
function stdin.or.args
    if test (count $argv) -eq 0
        cat /dev/stdin
    else
        echo $argv
    end

end
