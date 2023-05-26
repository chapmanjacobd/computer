# Defined interactively
function mv --wraps mv
    set parent (path dirname "$argv[-1]")
    if not path extension $argv[-1] >/dev/null; and not test -e "$parent"
        mkdir -p "$parent"
    end
    command mv $argv
end
