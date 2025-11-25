# Defined interactively
function lines.eval.split --argument-names cmd
    while read -l line
        echo "$line" | eval "$cmd"
    end
end
