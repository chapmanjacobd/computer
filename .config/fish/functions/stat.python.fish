# Defined interactively
function stat.python
    for f in $argv
        python -c "import os;from rich import inspect; inspect(os.stat('$f'))"
    end
end
