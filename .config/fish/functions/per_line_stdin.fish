# Defined interactively
function per_line_stdin --argument-names cmd
    while read -l line
        echo "$line" | eval "$cmd"
    end
end
