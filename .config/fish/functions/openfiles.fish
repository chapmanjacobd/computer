# Defined interactively
function openfiles
    sudo fatrace -f C | grep -vE '[CWO] /$|(deleted)'
end
