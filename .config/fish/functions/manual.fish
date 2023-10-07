# Defined via `source`
function manual
    cheat $argv | cat
    tldr $argv
    if confirm 'Open full manual?'
        man $argv
    end
end
