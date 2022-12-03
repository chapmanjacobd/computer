# Defined interactively
function recommit
    git reset --soft HEAD^
    git push -f
    wipm $argv
end
