# Defined interactively
function args.or.stdin
    if test (count $argv) -gt 0
        echo $argv
    else
        tee
    end

end
