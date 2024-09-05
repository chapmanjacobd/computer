function eval-file
    for j in (cat $argv)
        echo $j
        eval $j
    end
end
