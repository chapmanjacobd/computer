# Defined interactively
function json.keys.count
    jq -c 'keys | length'
end
