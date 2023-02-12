# Defined interactively
function not_in
    read | string split ' ' | combine - not $argv
end
