# Defined via `source`
function file
    if isatty stdin
        command file $argv
    else
        xargs -I FILE file -b FILE $argv
    end
end
