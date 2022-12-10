# Defined interactively
function seqn --argument first increment last
    set carr (seq $first $increment $last)
    for i in (seq 1 (count $carr))
        echo $carr[$i] $carr[(math "$i+1")]
    end
end
