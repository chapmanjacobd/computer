# Defined interactively
function lines.not.in.file
    read | string split ' ' | combine - not $argv
end
