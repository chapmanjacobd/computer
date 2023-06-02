# Defined interactively
function mecho
    if test (count $argv) -gt 0
        echo $argv
    else
        cat /dev/stdin
    end

end
