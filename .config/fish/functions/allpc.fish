# Defined interactively
function allpc
    for pc in pakon backup pulse15
        echo $pc
        ssh $pc $argv
        or $argv
    end
end
