# Defined via `source`
function lsof_fuser
    for pid in (fuser -m $argv &| awk '{for(i=3;i<=NF;i++){sub(/c$/,"",$i); print $i}}')
        lsof -p $pid | awk '$5=="REG" {print}' | grep -v mem
    end
end
