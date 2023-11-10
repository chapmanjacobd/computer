# Defined interactively
function openfiles
    sudo fatrace -f C $argv | grep -vE '[CWO] /$|(deleted)'
end
