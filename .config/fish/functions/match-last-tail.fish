# Defined interactively
function match-last-tail --argument pattern
    tac $argv[2] | sed '/'$pattern'/q' | tac
end
