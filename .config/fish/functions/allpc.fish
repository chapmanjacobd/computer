# Defined interactively
function allpc
    for pc in pakon backup len hk
        echo $pc
        ssh $pc $argv
        or $argv
    end
end
