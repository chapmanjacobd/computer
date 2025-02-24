# Defined interactively
function bracket_digits
    sed -E 's/.*\[([0-9]+)\].*/\1/'
end
