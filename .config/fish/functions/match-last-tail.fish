# Defined interactively
function match-last-tail --argument pattern
    tac | sed '/'$pattern'/q' $argv[2] | tac
end
