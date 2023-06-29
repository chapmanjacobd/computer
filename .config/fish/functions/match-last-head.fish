# Defined interactively
function match-last-head -a pattern
    tac $argv[2] | sed '0,/'$pattern'/d' | tac
end
