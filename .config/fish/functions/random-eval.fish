# Defined interactively
function random-eval
    set file (coalesce $argv[1] /dev/stdin)
    eval (shuf -n 1 $file)
end
