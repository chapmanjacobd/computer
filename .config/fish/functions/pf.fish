# Defined interactively
function pf
    set -l n $argv[1]

    for idx in (seq $n)
        b $argv[2..-1]
    end
end
