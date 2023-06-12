# Defined interactively
function sum
    set accumulator 0

    while read -l line
        set accumulator (math $accumulator+$line)
    end

    echo $accumulator
end
