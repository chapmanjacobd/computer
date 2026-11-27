# Defined interactively
function type.cat --wraps='cat'
    cat (command -v $argv)
end
