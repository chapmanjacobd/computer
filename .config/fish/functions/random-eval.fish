# Defined interactively
function random-eval
    set file (coalesce $argv[1] /dev/stdin)
    set cmd (shuf -n 1 $file) $argv[2..-1]
    echo $cmd
    eval $cmd
end
