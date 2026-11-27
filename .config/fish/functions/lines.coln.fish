# Defined interactively
function lines.coln
    set col $argv[1]
    if test $col -gt 0
        awk -v col=$col 'NF >= col { print $col }'
    else if test $col -lt 0
        awk -v col=$col 'NF >= -col { print $(NF + col + 1) }'
    end
end
