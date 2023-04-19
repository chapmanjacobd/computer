# Defined interactively
function mv
    if not path extension $argv[-1] >/dev/null; and not test -e $argv[-1]
        mkdir -p $argv[-1]
    end
    command mv $argv
end
