# Defined via `source`
function grep.csv --wraps='pee'
    pee 'head -1' "tail -n +1 | grep $argv"
end
