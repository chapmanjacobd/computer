# Defined interactively
function repeatdelay
    while $argv[2..-1]
        and sleep $argv[1]
    end
end
