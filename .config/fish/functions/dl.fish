# Defined interactively
function dl
    for j in (cat ~/.jobs/dl*.sh | shuf)
        echo $j
        repeat eval $j
    end
end
