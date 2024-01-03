# Defined interactively
function mv
    set parent (path dirname "$argv[-1]")
    if not path extension $argv[-1] >/dev/null; and not test -e "$parent"
        mkdir "$parent"
    end

    if test (count $argv) -eq 2
        rmdir "$argv[-1]"  # fast rename if possible
    end
    command mv $argv
end
