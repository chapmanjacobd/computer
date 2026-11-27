# Defined interactively
function seq.n --argument first increment last
    set -l values (seq $first $increment $last)
    set -l value_count (count $values)
    if test $value_count -lt 2
        return
    end

    for i in (seq 1 (math "$value_count - 1"))
        echo $values[$i] $values[(math "$i + 1")]
    end
end
