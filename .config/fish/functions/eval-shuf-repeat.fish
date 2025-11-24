# Defined interactively
function file.eval.shuf-repeat
    for j in (shuf $argv)
        echo $j
        repeat eval $j
    end
end
