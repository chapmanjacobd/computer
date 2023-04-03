# Defined interactively
function mv
    if not test -e $argv[-1]
        mkdir -p $argv[-1]
    end
    command mv $argv
end
