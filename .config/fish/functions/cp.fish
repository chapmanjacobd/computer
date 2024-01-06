# Defined interactively
function cp
    set parent (path dirname "$argv[-1]")
    if not path extension $argv[-1] >/dev/null; and not test -e "$parent"
        mkdir "$parent"
    end

    command cp $argv
end
