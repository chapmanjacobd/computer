# Defined interactively
function allpct
    for pc in pakon backup r730xd len hk
        ssh -t $pc $argv
    end
end
