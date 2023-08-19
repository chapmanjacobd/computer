# Defined interactively
function skip
    tail -n +(math 1+$argv[1]) $argv[2..-1]
end
