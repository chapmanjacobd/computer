# Defined interactively
function lines.sum.fish
    set accumulator 0

    while read -l line
        set accumulator (math $accumulator+$line)
    end

    echo $accumulator
end
