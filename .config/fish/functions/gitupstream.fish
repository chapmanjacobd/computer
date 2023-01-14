# Defined interactively
function gitupstream
    git branch --set-upstream-to=origin/$argv $argv
end
