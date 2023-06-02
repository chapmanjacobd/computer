# Defined interactively
function filetype
    if test (count $argv) -gt 0
        file -b $argv
    else
        xargs -I FILE file -b FILE $argv
    end

end
