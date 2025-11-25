# Defined interactively
function chars.numbers.brackets
    sed -E 's/.*\[([0-9]+)\].*/\1/' $argv
end
