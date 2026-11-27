# Defined interactively
function b --wraps='fish'
    fish -c (string join -- ' ' (string escape -- $argv)) &
end
