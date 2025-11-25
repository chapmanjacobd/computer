function file.eval.repeat
    for j in (cat $argv)
        echo $j
        repeat eval $j
    end
end
