# Defined interactively
function eachpc
    for pc in $servers
        sshpc $pc -t $argv
    end
end
