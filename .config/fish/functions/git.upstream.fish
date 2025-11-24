# Defined interactively
function git.upstream
    git branch --set-upstream-to=origin/$argv $argv
end
