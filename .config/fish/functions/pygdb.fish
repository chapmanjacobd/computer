# Defined interactively
function pygdb
    gdb --arg $(which python3) $argv
end
