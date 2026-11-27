# Defined via `source`
function timestamp --wraps='date' --description 'usage: timestamp 1 week ago'
    date +%s -d "$argv"
end
