# Defined interactively
function seq-eval
    for line in (cat $argv[1])
        set cmd $line $argv[2..-1]
        echo $cmd
        eval $cmd
    end
end
