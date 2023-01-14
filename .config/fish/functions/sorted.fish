# Defined via `source`
function sorted
    cat - | string trim | sort --unique --ignore-case
end
