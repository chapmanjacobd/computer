# Defined interactively
function manual
    tldr $argv
    cheat $argv
    if confirm 'Open full manual?'
        man $argv
    end
end
