# Defined interactively
function coln
    set col $argv[1]
    if test $col -gt 0
        awk '{print $'$argv[1]'}'
    else if test $col -lt 0
        awk 'NF && NF'$col' { print ( $(NF'$col') ) }'
    end
    awk '{print $(NF)}'
end
