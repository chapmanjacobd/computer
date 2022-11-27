# Defined via `source`
function trim
    for file in $argv
        awk -- '{$1=$1;print}' "$file" | sponge "$file"
    end
end
