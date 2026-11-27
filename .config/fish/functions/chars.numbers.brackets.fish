# Defined interactively
function chars.numbers.brackets --wraps='sed'
    sed -E 's/.*\[([0-9]+)\].*/\1/' $argv
end
