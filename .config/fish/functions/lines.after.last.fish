# Defined interactively
function lines.after.last --argument pattern
    tac $argv[2] | sed '/'$pattern'/q' | tac
end
