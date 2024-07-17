# Defined interactively
function allpc
    for pc in pakon backup pulse15
        ssh $pc $argv
        or $argv
    end
end
