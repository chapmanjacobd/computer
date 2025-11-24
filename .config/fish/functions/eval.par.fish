# Defined interactively
function eval.par
    parallel -N0 -j$argv[1] $argv[2..-1] ::: (seq 1 $argv[1])
end
