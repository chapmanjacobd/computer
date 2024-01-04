# Defined interactively
function mv
    set parent (path dirname "$argv[-1]")
    if not path extension $argv[-1] >/dev/null; and not test -e "$parent"
        mkdir "$parent"
    end

    if test (count $argv) -eq 2 -a (path basename $argv[1]) = (path basename $argv[2])
        rmdir "$argv[2]" >/dev/null # fast rename if possible
    end
    command mv $argv
end
