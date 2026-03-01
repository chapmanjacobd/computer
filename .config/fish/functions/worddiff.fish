# Defined via `source`
function worddiff
    diff (trU -s ' ' '\n' < $argv[1] | psub) (trU -s ' ' '\n' < $argv[2] | psub)
end
