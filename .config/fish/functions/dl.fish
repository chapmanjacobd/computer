# Defined interactively
function dl
    for j in (shuf $argv)
        echo $j
        repeat eval $j
    end
end
