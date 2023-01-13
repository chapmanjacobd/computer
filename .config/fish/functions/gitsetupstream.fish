# Defined interactively
function gitsetupstream
    git branch --set-upstream-to=origin/$argv $argv
end
