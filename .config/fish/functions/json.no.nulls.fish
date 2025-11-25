# Defined interactively
function json.no.nulls
    jq 'del(..|nulls)'
end
