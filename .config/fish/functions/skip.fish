# Defined interactively
function skip --wraps='tail'
    tail -n +(math 1+$argv[1]) $argv[2..-1]
end
