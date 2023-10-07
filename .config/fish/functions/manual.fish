# Defined via `source`
function manual
    cheat $argv
    tldr $argv
    if confirm 'Open full manual?'
        man $argv
    end
end
