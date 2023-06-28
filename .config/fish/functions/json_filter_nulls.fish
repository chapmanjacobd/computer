# Defined interactively
function json_filter_nulls
    jq 'del(..|nulls)'
end
