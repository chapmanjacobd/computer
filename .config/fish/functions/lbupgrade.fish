# Defined via `source`
function lbupgrade
    for pc in pakon backup pulse15
        ssh $pc pip install --upgrade xklb
        or pip install --upgrade xklb
    end
end
