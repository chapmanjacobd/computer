# Defined interactively
function paths.is.open
    sudo fatrace -f C $argv | grep -vE '[CWO] /$|(deleted)'
end
