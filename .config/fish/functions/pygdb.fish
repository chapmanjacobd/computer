# Defined interactively
function pygdb --wraps='gdb'
    gdb --arg $(which python3) $argv
end
