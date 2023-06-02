# Defined interactively
function filetype
    if isatty stdin
        file -b $argv
    else
        xargs -I FILE file -b FILE $argv
    end
end
