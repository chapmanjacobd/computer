# Defined interactively
function py_stat
    for f in $argv
        python -c "import os;from rich import inspect; inspect(os.stat('$f'))"
    end
end
