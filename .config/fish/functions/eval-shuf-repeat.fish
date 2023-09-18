# Defined interactively
function eval-shuf-repeat
    for j in (shuf $argv)
        echo $j
        repeat eval $j
    end
end
