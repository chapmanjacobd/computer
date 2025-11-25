# Defined interactively
function lines.until.last -a pattern
    tac $argv[2] | sed '0,/'$pattern'/d' | tac
end
