# Defined interactively
function paths.is.open --wraps='sudo'
    sudo fatrace -f C $argv | grep -vE '[CWO] /$|(deleted)'
end
