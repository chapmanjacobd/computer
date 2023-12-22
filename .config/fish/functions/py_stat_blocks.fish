# Defined interactively
function py_stat_blocks
    for f in $argv
        python -c "import os; print(os.stat('$f').st_blocks)"
    end
end
