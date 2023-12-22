# Defined interactively
function py_stat_size
    for f in $argv
        python -c "import os; print(os.path.getsize('$f'))"
    end
end
