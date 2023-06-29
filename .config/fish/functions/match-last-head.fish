# Defined interactively
function match-last-head -a pattern
    tac | sed '0,/'$pattern'/d' $argv[2] | tac
end
