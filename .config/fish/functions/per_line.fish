# Defined via `source`
function per_line --argument-names cmd
    while read -l line
        eval "$cmd" "$line"
    end
end
