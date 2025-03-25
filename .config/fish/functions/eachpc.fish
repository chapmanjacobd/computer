# Defined interactively
function eachpc
    for pc in pakon backup r730xd len hk
        sshpc $pc -t $argv
    end
end
