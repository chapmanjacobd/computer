# Defined via `source`
function lsof_fuser
    for pid in (fuser -m $argv &| awk '{for(i=3;i<=NF;i++){sub(/c$/,"",$i); print $i}}')
        lsof -p $pid | awk '$5=="REG" && $4!="mem" {print}'
    end
end
