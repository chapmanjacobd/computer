# Defined via `source`
function csv_grep
    pee 'head -1' "tail -n +1 | grep $argv"
end
