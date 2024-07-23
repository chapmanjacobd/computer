# Defined interactively
function par
    parallel -N0 -j$argv[1] $argv[2..-1] ::: {1..$argv[1]}
end
