# Defined interactively
function enumerate
    set -l count 1
    for arg in $argv
        echo $count\t$arg
        set count (math $count + 1)
    end
end
