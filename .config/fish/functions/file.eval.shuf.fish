# Defined interactively
function file.eval.shuf
    for j in (shuf $argv)
        echo $j
        eval $j
    end
end
