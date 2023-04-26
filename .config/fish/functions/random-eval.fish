# Defined interactively
function random-eval
    set file (coalesce $argv[1] /dev/stdin)
    set cmd (shuf -n 1 $file)
    echo $cmd
    eval $cmd
end
