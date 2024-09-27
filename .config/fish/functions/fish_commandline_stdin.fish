# Defined interactively
function fish_commandline_stdin
    while read -l line
        commandline -a $line
    end
    commandline -C (commandline | string length)
end
