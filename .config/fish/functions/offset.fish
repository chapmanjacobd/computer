# Defined interactively
function offset --wraps='tail'
    tail -n +(math 1+$argv[1]) $argv[2..]
end
