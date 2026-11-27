# Defined interactively
function callback --wraps='fish'
    fish
    string length -q -- $argv; and $argv
end
