# Defined interactively
function mecho
    if test (count $argv) -gt 0
        echo $argv
    else
        tee
    end

end
