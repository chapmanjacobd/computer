# Defined interactively
function commandline.stdin
    while read -l line
        commandline -a $line
    end
    commandline -C (commandline | string length)
end
