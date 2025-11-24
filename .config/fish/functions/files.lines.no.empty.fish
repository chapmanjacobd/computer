# Defined via `source`
function files.lines.no.empty
    for file in $argv
        awk -- '{$1=$1;print}' "$file" | sponge "$file"
    end
end
