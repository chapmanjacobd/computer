# Defined via `source`
function worddiff
    diff (tr.unicode -s ' ' '\n' < $argv[1] | psub) (tr.unicode -s ' ' '\n' < $argv[2] | psub)
end
