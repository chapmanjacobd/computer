# Defined interactively
function allpct
    for pc in $servers
        ssh -t $pc $argv
    end
end
